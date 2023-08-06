import math
import random
import pytest
import time
import tornado.testing

from statistics import mean, median, stdev
from tornado.ioloop import IOLoop

from tinybird.sql_template import get_template_and_variables
from tinybird.sql_toolset import replace_tables_chquery_cached, sql_get_used_tables_cached
from tinybird.token_scope import scopes
from tinybird.user import Users, User

from .conftest import is_main_process
from .views.base_test import BaseTest


def get_cache_info():
    hits, misses, _, _ = get_template_and_variables.cache_info()
    return hits, misses


def flush_all_caches():
    get_template_and_variables.cache_clear()
    sql_get_used_tables_cached.cache_clear()
    replace_tables_chquery_cached.cache_clear()


@pytest.mark.serial  # Better to test this serially (better to move it elsewhere too). It changes the cache status too
@pytest.mark.skipif(not is_main_process(), reason="Serial test")
class TestPerformance(BaseTest):
    ITERATIONS = 80

    def check_timings(self, timings, max_mean: float, max_p90: float, max_min: float):
        min_timings = min(timings)
        mean_timings = mean(timings)
        stdev_timings = stdev(timings)
        median_timings = median(timings)
        p90_timings = sorted(timings)[math.ceil(self.ITERATIONS * .9) - 1]
        print(f"""Timing metrics:
            min    {min_timings:.5f}
            mean   {mean_timings:.5f}
            stdev  {stdev_timings:.5f}
            median {median_timings:.5f}
            p90    {p90_timings:.5f}""")

        self.assertTrue(min_timings < max_min, f'Invalid min time performance: {min_timings} < {max_min}')
        self.assertTrue(mean_timings < max_mean, f'Invalid mean time performance: {mean_timings} < {max_mean}')
        self.assertTrue(p90_timings < max_p90, f'Invalid P90 time performance: {p90_timings} < {max_p90}')

    async def replace_tables_with_options(self, flush=True, randomize=None, sync=False):
        if flush:
            # Note that this only works correctly because we have only one runner
            await IOLoop.current().run_in_executor(User.replace_executor, flush_all_caches)

        if randomize:
            self.variables[randomize] = f"{random.randint(0, 1000000000)}"

        start = time.time()
        if sync:
            _ = self.u.replace_tables(f'SELECT * FROM {self.pipe.id}',
                                      readable_resources=self.readable_resources,
                                      pipe=self.pipe,
                                      use_pipe_nodes=False,
                                      variables=self.variables,
                                      template_execution_results=self.template_execution_results)
        else:
            _ = await self.u.replace_tables_async(f'SELECT * FROM {self.pipe.id}',
                                                  readable_resources=self.readable_resources,
                                                  pipe=self.pipe,
                                                  use_pipe_nodes=False,
                                                  variables=self.variables,
                                                  template_execution_results=self.template_execution_results)
        return time.time() - start

    async def get_replace_timings(self, flush=False, randomize=None):
        times = []
        for _i in range(self.ITERATIONS):
            t = await self.replace_tables_with_options(flush=flush, sync=False, randomize=randomize)
            times.append(t)
        return times

    @tornado.testing.gen_test(timeout=360)
    async def test_template_cache_random_parameter(self):

        datasources = [
            'article_commercial_tags_join_global_parent_partnumber',
            'articles_commercial_tags',
            'articles_filters',
            'articles_join',
            'articles_join_global_partnumber',
            'datetime_lut',
            'product_rank_month_mt',
            'product_rank_mt',
            'product_rank_rt_mt',
            'sales_historic_landing',
            'sales_historic_last_date',
            'sales_rt',
            'stores',
            'stores_join',
            'tagging_array',
            'worldwide_stores',
            'worldwide_stores_join_by_country',
        ]

        nodes = [
            {
                'name': 'all_stores',
                'sql': '''SELECT *
                FROM stores
                UNION ALL
                SELECT *
                FROM worldwide_stores '''
            },
            {
                'name': 'by_timestamp',
                'sql': '''%
                with
                    {% comment "prepare a map purchase_location -> offset to be used in query" %}
                    (
                        select length(location) > 0 ? location: [0] from (
                            select groupArray(location) location from (select * from stores order by cod_store)
                        )
                    ) as countries,
                    (
                        select length(offsets) > 0 ? offsets: [0] from (
                            select groupArray(-offset) offsets from
                            (select timezone from stores order by cod_store)
                            any left join
                            (select timezone, offset from datetime_lut where date = toDate(now()))
                            using timezone
                        )
                    ) as timezones
                SELECT
                cast(sku_rank_lc as String) sku_rank_lc,
                groupUniqArrayState(parent_catentry) as parent_catentry_array,
                {% for last, x in enumerate_with_last(split_to_array(attr, 'amount_return')) %}
                {% if x == 'order_count' %}
                        toInt64(uniq(cod_order_wcs)) as order_count,
                {% elif x.startswith('amount') %}
                        sumIf(amount * joinGet({{TABLE('stores_join', quote="'")}}, 'exchange_rate', toInt32(purchase_location))
                        ,
                            cod_transaction IN
                            {{ {'net': (72, 772, 73, 808), 'net_req': (72, 772, -73, -808), 'return': (73, 808), 'gross': (72, 772), 'return_req': (-73, -808) }[x.split('_', 1)[1]] }}
                        )
                {% elif x.startswith('units') %}
                        toInt64(sumIf(units, cod_transaction IN
                            {{ { 'net': (72, 772, 73, 808), 'net_req': (72, 772, -73, -808), 'return': (73, 808), 'gross': (72, 772), 'return_req': (-73, -808) }[x.split('_', 1)[1]] }}
                        ))
                {% end %}
                as {{symbol(x)}}
                {% if not last %},{% end %}
                {% end %}
                FROM (
                    WITH (select max(last_date) from sales_historic_last_date) as split_date
                    select cod_brand, sku_rank_lc, local_timeplaced, purchase_location, amount, cod_order_wcs, cod_transaction, units, cod_device, parent_catentry
                    {% if defined(commercial_tag) %}
                        ,
                        {% comment "this is a double join because the commercial tags filter" %}
                        joinGet({{TABLE('article_commercial_tags_dates_join', quote="'")}}, 'date_range',
                            concat(
                                joinGet({{TABLE('stores_join', quote="'")}}, 'country', toInt32(purchase_location)),
                                '_',
                                joinGet({{TABLE('articles_join', quote="'")}}, 'parent_partnumber', sku_rank_lc),
                                '_',
                                {{commercial_tag}}
                            )
                        ) as tag_range
                    {% end %}
                    from sales_rt
                    PREWHERE
                        local_timeplaced between toDateTime(toDate({{Date(date_start)}})) and toDateTime(toDate({{Date(date_end)}}) + 1) - 1
                    WHERE
                        local_timeplaced > toDateTime(split_date)
                        {% if defined(commercial_tag) %}
                            and local_timeplaced between toDateTime(tag_range[1]) and toDateTime(tag_range[2] + 1) - 1
                        {% end %}
                    and (cod_status <> 'X' or cod_status is null) and replacement = 0
                    {% comment "moved country filters here because there is an index by purchase_location" %}
                    {% if defined(country) or defined(cod_brand) %}
                        and purchase_location in (SELECT toInt16(location) from all_stores
                            where {{sql_and(country__in=Array(country, defined=False), cod_brand__in=Array(cod_brand, 'Int32', defined=False))}})
                    {% end %}
                    {% if defined(purchase_location) %}
                        and purchase_location in {{Array(purchase_location, 'Int32')}}
                    {% end %}
                    {% if defined(cod_order_type) %}
                        and cod_order_type = {{Int32(cod_order_type)}}
                    {% end %}
                    UNION ALL
                    WITH (select max(last_date) from sales_historic_last_date) as split_date
                    select cod_brand,CAST(sku_rank AS LowCardinality(String)) sku_rank_lc,local_timeplaced, purchase_location, amount, cod_order_wcs, cod_transaction, units, cod_device, parent_catentry
                    {% if defined(commercial_tag) %}
                        ,
                        {% comment "this is a double join because the commercial tags filter" %}
                        joinGet({{TABLE('article_commercial_tags_dates_join', quote="'")}}, 'date_range',
                            concat(
                                joinGet({{TABLE('stores_join', quote="'")}}, 'country', toInt32(purchase_location)),
                                '_',
                                joinGet({{TABLE('articles_join', quote="'")}}, 'parent_partnumber', sku_rank),
                                '_',
                                {{commercial_tag}}
                            )
                        ) as tag_range
                    {% end %}
                    from sales_historic_landing
                    WHERE
                        local_timeplaced between toDateTime(toDate({{Date(date_start)}})) and toDateTime(toDate({{Date(date_end)}}) + 1) - 1
                        and local_timeplaced <= toDateTime(split_date)
                        {% if defined(commercial_tag) %}
                            and local_timeplaced between toDateTime(tag_range[1]) and toDateTime(tag_range[2] + 1) - 1
                        {% end %}
                    and (cod_status <> 'X' or cod_status is null) and replacement = 0
                    {% comment "moved country filters here because there is an index by purchase_location" %}
                    {% if defined(country) or defined(cod_brand) %}
                        and purchase_location in (SELECT toInt16(location) from all_stores
                            where {{sql_and(country__in=Array(country, defined=False), cod_brand__in=Array(cod_brand, 'Int32', defined=False))}})
                    {% end %}
                    {% if defined(purchase_location) %}
                        and purchase_location in {{Array(purchase_location, 'Int32')}}
                    {% end %}
                    {% if defined(cod_order_type) %}
                        and cod_order_type = {{Int32(cod_order_type)}}
                    {% end %}
                )
                WHERE local_timeplaced + transform(purchase_location, arrayConcat([0], countries), arrayConcat([0], timezones)) < {% if end_ts_utc == 'now' %} now() {% else %} {{DateTime(end_ts_utc, '2019-01-01 00:00:00')}} {% end %}
                -- cod_device filter (optional)
                {% if defined(cod_device) %}
                    and cod_device in {{Array(cod_device)}}
                {% end %}
                {% if defined(cod_section) or defined(cod_product) or defined(cod_family) or defined(campaign) or defined(cod_product_line) or defined(cod_subfamily) or defined(partnumber) %}
                    and concat(
                        toString(cod_brand),
                        sku_rank_lc
                    ) in (
                        select concat(toString(cod_brand), sku_rank_lc) from {{TABLE('articles_filters')}}
                        prewhere 1
                        {% if defined(cod_section) or defined(cod_product) or defined(cod_family) or defined(campaign) or defined(cod_product_line) or defined(cod_subfamily) %}
                            AND {{sql_and(cod_section__in=Array(cod_section, 'Int',defined=False), cod_product__in=Array(cod_product,'Int', defined=False),cod_family__in=Array(cod_family, 'Int', defined=False), campaign__in=Array(campaign, defined=False), cod_product_line__in=Array(cod_product_line, 'Int', defined=False), cod_subfamily__in=Array(cod_subfamily, 'Int', defined=False))}}
                        {% end %}
                        {% if defined(country) or defined(cod_brand) %}
                            and cod_brand in (
                                SELECT cod_brand from all_stores
                                where {{sql_and(country__in=Array(country, defined=False), cod_brand__in=Array(cod_brand, 'Int32', defined=False))}}
                            )
                        {% end %}
                        {% if defined(partnumber) %}
                        AND
                            {% if not defined(campaign) %}
                                global_parent_partnumber
                            {% else %}
                                parent_partnumber
                            {% end %}
                            like {{partnumber}}
                        {% end %}
                    )
                {% end %}
                {% if defined(tags) %}
                and parent_catentry in (select parent_catentry from {{TABLE('tagging')}} where tag in {{Array(tags)}})
                {% end %}
                group by sku_rank_lc'''
            },
            {
                'name': 'historic',
                'sql': '''%
                    WITH (select max(last_date) from sales_historic_last_date) as split_date
                    SELECT
                        cast(sku_rank_lc as String) sku_rank_lc,
                        parent_catentry_array,
                        purchase_location,
                        {% if defined(commercial_tag) %}
                            {% comment "this is a double join because the commercial tags filter" %}
                            joinGet({{TABLE('article_commercial_tags_dates_join', quote="'")}}, 'date_range',
                                concat(
                                    joinGet({{TABLE('stores_join', quote="'")}}, 'country', toInt32(purchase_location)),
                                    '_',
                                    joinGet({{TABLE('articles_join', quote="'")}}, 'parent_partnumber', sku_rank_lc),
                                    '_',
                                    {{commercial_tag}}
                                )
                            ) as tag_range,
                        {% end %}
                        {% for last, x in enumerate_with_last(split_to_array(attr, 'amount_return')) %}
                        {% if not defined(cod_device) %}
                            {{symbol(x)}}
                            {% if x.startswith('amount') %}
                                    * joinGet({{TABLE('stores_join', quote="'")}}, 'exchange_rate', toInt32(purchase_location))
                            {% end %}
                        {% else %}
                            {% if x == 'order_count' %}
                            toInt32(arraySum(
                                arrayFilter(
                                    (order_wcs, device_hash) -> device_hash IN (select arrayJoin(arrayMap(x -> reinterpretAsUInt64(x), {{split_to_array(cod_device, '')}}))),
                                    `OrderMap.orders`,
                                    `OrderMap.cod_device_hash`
                                )
                            ))
                            {% else %}
                                arraySum(
                                    arrayFilter(
                                        (amount, cod_tx, device_hash) ->
                                            cod_tx IN {{ {'net': (72, 772, 73, 808), 'net_req': (72, 772, -73, -808), 'return': (73, 808), 'gross': (72, 772), 'return_req': (-73, -808) }[x.split('_', 1)[1]] }}
                                            and
                                            device_hash IN (select arrayJoin(arrayMap(x -> reinterpretAsUInt64(x), {{split_to_array(cod_device, '')}}))),
                                        {% if x.startswith('amount') %}
                                        `DeviceMap.amount`,
                                        {% else %}
                                        `DeviceMap.units`,
                                        {% end %}
                                        `DeviceMap.cod_transaction_Key`,
                                        `DeviceMap.cod_device_hash`
                                    )
                                )
                                {% if x.startswith('amount') %}
                                        * joinGet({{TABLE('stores_join', quote="'")}}, 'exchange_rate', toInt32(purchase_location))
                                {% end %}
                            {% end %}
                        {% end %}
                        as {{symbol(x)}}
                        {% if not last %},{% end %}
                        {% end %}
                    FROM
                    {% if defined(cod_order_type) %}
                        {{TABLE('product_rank_sint_mt')}}
                    {% else %}
                        {{TABLE('product_rank_mt')}}
                    {% end %}
                    WHERE
                        date between {{Date(date_start)}} and {{Date(date_end)}}
                        and date <= split_date
                        {% if not defined(commercial_tag) %}
                        and not date between
                            addMonths(
                                toStartOfMonth(toDate({{Date(date_start)}})),
                                if(toStartOfMonth(toDate({{Date(date_start)}})) = toDate({{Date(date_start)}}), 0, 1)
                            )
                            and
                            addMonths(
                                toStartOfMonth(toDate({{Date(date_end)}})),
                                if(toStartOfMonth(toDate({{Date(date_end)}})) = toStartOfMonth(toDate({{Date(date_end)}}) + 1), 0, 1)
                            ) - 1
                        {% else %}
                            and date between tag_range[1] and tag_range[2]
                        {% end %}
                    -- country filter
                    {% if defined(country) or defined(cod_brand) %}
                        and purchase_location in (SELECT toUInt16(location) from all_stores
                        where {{sql_and(country__in=Array(country, defined=False), cod_brand__in=Array(cod_brand, 'Int32', defined=False))}})
                    {% end %}
                    {% if defined(purchase_location) %}
                        and purchase_location in {{Array(purchase_location, 'Int32')}}
                    {% end %}'''
            },
            {
                'name': 'historic_month',
                'sql': '''%
                    WITH (select max(last_date) from sales_historic_last_date) as split_date
                    SELECT
                        sku_rank_lc,
                        parent_catentry_array,
                        purchase_location,
                        {% if defined(commercial_tag) %}
                            {% comment "this is a double join because the commercial tags filter" %}
                            joinGet({{TABLE('article_commercial_tags_dates_join', quote="'")}}, 'date_range',
                                concat(
                                    joinGet({{TABLE('stores_join', quote="'")}}, 'country', toInt32(purchase_location)),
                                    '_',
                                    joinGet({{TABLE('articles_join', quote="'")}}, 'parent_partnumber', sku_rank_lc),
                                    '_',
                                    {{commercial_tag}}
                                )
                            ) as tag_range,
                        {% end %}
                        {% for last, x in enumerate_with_last(split_to_array(attr, 'amount_return')) %}
                        {% if not defined(cod_device) %}
                            {{symbol(x)}}
                            {% if x.startswith('amount') %}
                                    * joinGet({{TABLE('stores_join', quote="'")}}, 'exchange_rate', toInt32(purchase_location))
                            {% end %}
                        {% else %}
                            {% if x == 'order_count' %}
                            toInt32(arraySum(
                                arrayFilter(
                                    (order_wcs, device_hash) -> device_hash IN (select arrayJoin(arrayMap(x -> reinterpretAsUInt64(x), {{split_to_array(cod_device, '')}}))),
                                    `OrderMap.orders`,
                                    `OrderMap.cod_device_hash`
                                )
                            ))
                            {% else %}
                                arraySum(
                                    arrayFilter(
                                        (amount, cod_tx, device_hash) ->
                                            cod_tx IN {{ {'net': (72, 772, 73, 808), 'net_req': (72, 772, -73, -808), 'return': (73, 808), 'gross': (72, 772), 'return_req': (-73, -808) }[x.split('_', 1)[1]] }}
                                            and
                                            device_hash IN (select arrayJoin(arrayMap(x -> reinterpretAsUInt64(x), {{split_to_array(cod_device, '')}}))),
                                        {% if x.startswith('amount') %}
                                        `DeviceMap.amount`,
                                        {% else %}
                                        `DeviceMap.units`,
                                        {% end %}
                                        `DeviceMap.cod_transaction_Key`,
                                        `DeviceMap.cod_device_hash`
                                    )
                                )
                                {% if x.startswith('amount') %}
                                        * joinGet({{TABLE('stores_join', quote="'")}}, 'exchange_rate', toInt32(purchase_location))
                                {% end %}
                            {% end %}
                        {% end %}
                        as {{symbol(x)}}
                        {% if not last %},{% end %}
                        {% end %}
                    FROM
                    {% if defined(cod_order_type) %}
                        {{TABLE('product_rank_sint_month_mt')}}
                    {% else %}
                        {{TABLE('product_rank_month_mt')}}
                    {% end %}
                    WHERE
                        date BETWEEN
                            addMonths(
                                toStartOfMonth(toDate({{Date(date_start)}})),
                                if(toStartOfMonth(toDate({{Date(date_start)}})) = toDate({{Date(date_start)}}), 0, 1)
                            )
                            and
                            addMonths(
                                toStartOfMonth(toDate({{Date(date_end)}})),
                                if(toStartOfMonth(toDate({{Date(date_end)}})) = toStartOfMonth(toDate({{Date(date_end)}}) + 1), 0, 1)
                            ) - 1
                            {% if defined(commercial_tag) %}
                                and date between tag_range[1] and tag_range[2]
                            {% end %}
                    -- country filter
                    {% if defined(country) or defined(cod_brand) %}
                        and purchase_location in (SELECT toUInt16(location) from all_stores
                        where {{sql_and(country__in=Array(country, defined=False), cod_brand__in=Array(cod_brand, 'Int32', defined=False))}})
                    {% end %}
                    {% if defined(purchase_location) %}
                        and purchase_location in {{Array(purchase_location, 'Int32')}}
                    {% end %}'''
            },
            {
                'name': 'rt',
                'sql': '''%
                    WITH (select max(last_date) from sales_historic_last_date) as split_date
                    SELECT
                        cast(sku_rank_lc as String) sku_rank_lc,
                        parent_catentry_array,
                        purchase_location,
                        {% if defined(commercial_tag) %}
                            {% comment "this is a double join because the commercial tags filter" %}
                            joinGet({{TABLE('article_commercial_tags_dates_join', quote="'")}}, 'date_range',
                                concat(
                                    joinGet({{TABLE('stores_join', quote="'")}}, 'country', toInt32(purchase_location)),
                                    '_',
                                    joinGet({{TABLE('articles_join', quote="'")}}, 'parent_partnumber', sku_rank_lc),
                                    '_',
                                    {{commercial_tag}}
                                )
                            ) as tag_range,
                        {% end %}
                        {% for last, x in enumerate_with_last(split_to_array(attr, 'amount_return')) %}
                        {% if not defined(cod_device) %}
                            {{symbol(x)}}
                            {% if x.startswith('amount') %}
                                    * joinGet({{TABLE('stores_join', quote="'")}}, 'exchange_rate', toInt32(purchase_location))
                            {% end %}
                        {% else %}
                            {% if x == 'order_count' %}
                            toInt32(arraySum(
                                arrayFilter(
                                    (order_wcs, device_hash) -> device_hash IN (select arrayJoin(arrayMap(x -> reinterpretAsUInt64(x), {{split_to_array(cod_device, '')}}))),
                                    `OrderMap.orders`,
                                    `OrderMap.cod_device_hash`
                                )
                            ))
                            {% else %}
                                arraySum(
                                    arrayFilter(
                                        (amount, cod_tx, device_hash) ->
                                            cod_tx IN {{ {'net': (72, 772, 73, 808), 'net_req': (72, 772, -73, -808), 'return': (73, 808), 'gross': (72, 772), 'return_req': (-73, -808) }[x.split('_', 1)[1]] }}
                                            and
                                            device_hash IN (select arrayJoin(arrayMap(x -> reinterpretAsUInt64(x), {{split_to_array(cod_device, '')}}))),
                                        {% if x.startswith('amount') %}
                                        `DeviceMap.amount`,
                                        {% else %}
                                        `DeviceMap.units`,
                                        {% end %}
                                        `DeviceMap.cod_transaction_Key`,
                                        `DeviceMap.cod_device_hash`
                                    )
                                )
                                {% if x.startswith('amount') %}
                                        * joinGet({{TABLE('stores_join', quote="'")}}, 'exchange_rate', toInt32(purchase_location))
                                {% end %}
                            {% end %}
                        {% end %}
                        as {{symbol(x)}}
                        {% if not last %},{% end %}
                        {% end %}
                    FROM
                    {% if defined(cod_order_type) %}
                        {{TABLE('product_rank_rt_sint_mt')}}
                    {% else %}
                        {{TABLE('product_rank_rt_mt')}}
                    {% end %}
                    WHERE date between {{Date(date_start)}} and {{Date(date_end)}} and date > split_date
                    {% if defined(commercial_tag) %}
                        and date between tag_range[1] and tag_range[2]
                    {% end %}
                    -- country filter
                    {% if defined(country) or defined(cod_brand) %}
                        and purchase_location in (SELECT toUInt16(location) from all_stores
                        where {{sql_and(country__in=Array(country, defined=False), cod_brand__in=Array(cod_brand, 'Int32', defined=False))}})
                    {% end %}
                    {% if defined(purchase_location) %}
                        and purchase_location in {{Array(purchase_location, 'Int32')}}
                    {% end %}'''
            },
            {
                'name': 'rank',
                'sql': '''%
                    SELECT
                        joinGet({{TABLE('articles_join', quote="'")}},
                            {% if not defined(campaign) %}
                                'global_parent_partnumber'
                            {% else %}
                                'parent_partnumber'
                            {% end %}, sku_rank_lc) product_rank,
                        groupUniqArray(sku_rank_lc) children,
                        groupUniqArrayMerge(parent_catentry_array) as parent_catentry_array,
                        {% for last, x in  enumerate_with_last(split_to_array(attr, 'amount_return')) %}
                            sum({{symbol(x)}}) as {{symbol(x)}}
                            {% if not last %},{% end %}
                        {% end %}
                    FROM
                    (
                        select * from (
                            {% if defined(end_ts_utc) %}
                                SELECT * FROM by_timestamp
                            {% else %}
                                SELECT * from historic
                                UNION ALL
                                SELECT * from rt
                                {% if not defined(commercial_tag) %}
                                UNION ALL
                                SELECT * from historic_month
                                {% end %}
                            {% end %}
                        )
                        {% if not defined(end_ts_utc) %}
                        WHERE 1
                        {% if defined(cod_section) or defined(cod_product) or defined(cod_family) or defined(campaign) or defined(cod_product_line) or defined(cod_subfamily) or defined(partnumber) %}
                            and concat(
                                toString(joinGet({{TABLE('stores_join', quote="'")}}, 'cod_brand', toInt32(purchase_location))),
                                sku_rank_lc
                            ) in (
                                select concat(toString(cod_brand), sku_rank_lc) from {{TABLE('articles_filters')}}
                                prewhere 1
                                {% if defined(cod_section) or defined(cod_product) or defined(cod_family) or defined(campaign) or defined(cod_product_line) or defined(cod_subfamily) %}
                                    AND {{sql_and(cod_section__in=Array(cod_section, 'Int',defined=False), cod_product__in=Array(cod_product,'Int', defined=False),cod_family__in=Array(cod_family, 'Int', defined=False), campaign__in=Array(campaign, defined=False), cod_product_line__in=Array(cod_product_line, 'Int', defined=False), cod_subfamily__in=Array(cod_subfamily, 'Int', defined=False))}}
                                {% end %}
                                {% if defined(country) or defined(cod_brand) %}
                                    and cod_brand in (
                                        SELECT distinct cod_brand from all_stores
                                        where {{sql_and(country__in=Array(country, defined=False), cod_brand__in=Array(cod_brand, 'Int32', defined=False))}}
                                    )
                                {% end %}
                                {% if defined(partnumber) %}
                                AND
                                    {% if not defined(campaign) %}
                                        global_parent_partnumber
                                    {% else %}
                                        parent_partnumber
                                    {% end %}
                                    like {{partnumber}}
                                {% end %}
                            )
                        {% end %}
                        {% end %}
                    )
                    WHERE product_rank != ''
                    GROUP BY product_rank
                    {% if defined(tags) %}
                    having arraySum(arrayMap(x -> toInt64(x) in (select parent_catentry from {{TABLE('tagging')}} where tag in {{Array(tags)}}) ? 1: 0,
                        parent_catentry_array
                    )) > 0
                    {% end %}
                    ORDER BY {{symbol(split_to_array(attr, 'amount_return')[0])}}
                        {% if defined(sort) and sort.lower() == 'asc' %}
                        ASC
                        {% else %}
                        DESC
                        {% end %}
                    LIMIT {{Int32(page_size, 32)}}
                    OFFSET {{Int32(page, 0) * Int32(page_size, 32)}}'''
            },
            {
                'name': 'sales_in_units_and_amount_by_country',
                'sql': '''%
                {% if defined(commercial_tag) %}
                    {{max_threads(10)}}
                {% else %}
                    {{max_threads(8)}}
                {% end %}
                SELECT
                        product_rank as sku,
                        {% if not defined(campaign) %}
                        joinGet({{TABLE('articles_join_global_partnumber', quote="'")}}, 'image', product_rank) as image,
                        joinGet({{TABLE('articles_join_global_partnumber', quote="'")}}, 'plain_image', product_rank) as plain_image,
                        joinGet({{TABLE('articles_join_global_partnumber', quote="'")}}, 'description', product_rank) as description
                        {% else %}
                        joinGet({{TABLE('articles_join_parent_partnumber', quote="'")}}, 'image', product_rank) as image,
                        joinGet({{TABLE('articles_join_parent_partnumber', quote="'")}}, 'plain_image', product_rank) as plain_image,
                        joinGet({{TABLE('articles_join_parent_partnumber', quote="'")}}, 'description', product_rank) as description
                    {% end %},
                    arrayMap(
                        x -> joinGet({{TABLE('articles_join', quote="'")}}, 'parent_partnumber', x),
                        children
                    ) as partnumbers,
                    arrayDistinct(
                    arrayFilter(
                        x -> x != '',
                        arrayFlatten(
                            arrayMap(x-> joinGet('tagging_array', 'tags', toInt64(x)), parent_catentry_array)
                        )
                    )
                    ) as tags,
                    arrayDistinct(arrayFilter(
                        x ->
                            -- {tag} -> x.1, {country} -> x.2, {start_date} -> x.3, {end_date} -> x.4
                            -- this is the basic algorithm to check if 1d segments overlap: https://eli.thegreenplace.net/2008/08/15/intersection-of-1d-segments
                            {{Date(date_end)}} >= x.3 and  x.4 >= {{Date(date_start)}}
                            {% if defined(country) %} and x.2 in {{Array(country)}} {% end %}
                            {% if defined(commercial_tag) %} and x.1 in {{Array(commercial_tag)}} {% end %},
                    arrayMap(x -> arrayMap(country, start_date, end_date, tag -> (tag, country, start_date, end_date), x.1, x.2, x.3, x.4) ,
                        arrayMap(partnumber ->
                        {% if not defined(campaign) %}
                        joinGet({{TABLE('article_commercial_tags_join_global_parent_partnumber', quote="'")}}, 'groupped_fields', partnumber),
                        {% else %}
                        joinGet({{TABLE('article_commercial_tags_join_parent_partnumber', quote="'")}}, 'groupped_fields', partnumber),
                        {% end %}
                        partnumbers
                        )
                    )[1]
                    )) commercial_tags,
                    {% for last, x in  enumerate_with_last(split_to_array(attr, 'amount_return')) %}
                        {{symbol(x)}}
                        {% if not last %},{% end %}
                    {% end %}
                    FROM rank
                    {% if defined(symbol) %}
                        WHERE sku == {{String(symbol)}}
                    {% end %}
                    '''
            }]

        pipe_name = 'example'
        token_name = 'example endpoint api'
        u = Users.get_by_id(self.WORKSPACE_ID)
        with User.transaction(u.id) as user:
            for ds_name in datasources:
                user.add_datasource(ds_name)
            pipe = user.add_pipe(pipe_name, nodes=nodes)
            pipe.endpoint = pipe.pipeline.nodes[-1].id
            user.update_pipe(pipe)
            user.add_token(token_name, scopes.PIPES_READ, pipe.id)

        self.u = Users.get_by_id(self.WORKSPACE_ID)
        self.variables = {
            'date_start': '2020-09-03',
            'date_end': '2020-09-03',
            'attr': 'order_count',
            'cod_section': '1',
            'cod_brand': '1,16',
            'page': '0',
            'page_size': '200',
        }

        self.pipe = self.u.get_pipe(pipe_name)
        self.template_execution_results = {}
        access_info = self.u.get_token_access_info(token_name)
        self.readable_resources = access_info.get_resources_for_scope(scopes.DATASOURCES_READ, scopes.PIPES_READ)

        self.assertEqual(User.replace_executor._max_workers, 1, "This test is designed for 1 worker only")

        await self.replace_tables_with_options(flush=False, randomize=None, sync=False)  # Ensure warmup (for processes)
        await IOLoop.current().run_in_executor(User.replace_executor, flush_all_caches)
        timings_with_cache = await self.get_replace_timings(flush=False, randomize='cod_section')

        hits, misses = await IOLoop.current().run_in_executor(User.replace_executor, get_cache_info)
        self.assertEqual(misses, 5)
        self.assertEqual(hits, 5 * (self.ITERATIONS - 1))

        total_cached = sum(timings_with_cache)
        print(f"Total with cache: {total_cached}")
        self.check_timings(timings_with_cache, max_mean=.08, max_p90=.09, max_min=.07)

        timings_without_cache = await self.get_replace_timings(flush=True, randomize='cod_section')

        total_without_cache = sum(timings_without_cache)
        print(f"Total without cache: {total_without_cache}")
        self.check_timings(timings_without_cache, max_mean=.16, max_p90=.18, max_min=.14)

        improvement = total_without_cache / total_cached
        print(f"Improvement: {improvement:.3f}x")
        self.assertGreater(improvement, 1.5, "Timings with cache should be much faster than without it")

    @tornado.testing.gen_test(timeout=360)
    async def test_toolset_cache_constant_parameter(self):

        datasources = [
            "prd_rawdata.ds_stm_wpv",
            "prd_benchdirect.currencies_exchange_join",
            "prd_rawdata.ds_mv_currencies_join__v1",
            "prd_rawdata.ds_org_currencies_historical_join",
            "fingerprint_property_total_origins",
            "fingerprint_property_group_by_day",
            "fingerprint_group_by_day",
            "property_grouped",
            "fingerprint_grouped",
            "fingerprint_chain_grouped",
            "prd_rawdata.ds_stm_events__v1",
            "fingerprint_property_group_by_tool",
            "fingerprint_chain_group_by_tool",
            "prd_rawdata.ds_mv_partner_hotels_join_by_property_id__v2",
            "prd_rawdata.ds_mv_pages_join_by_id__v2",
            "fingerprint_property_group_by_toolgroup",
            "prd_rawdata.ds_db_toolgroup_tools",
            "fingerprint_corporative_grouped",
            "fingerprint_property_grouped",
            "fingerprint_corporative_group_by_day",
            "fingerprint_corporative_group_by_tool",
            "fingerprint_corporative_group_by_toolgroup",
            "ds_test",
            "booking_ids",
            "fingerprint_chain_group_by_day",
            "browser_version_group_by_day",
            "browser_group_by_day",
            "country_group_by_day",
            "device_group_by_day",
            "geoname_group_by_day",
            "language_group_by_day",
            "network_group_by_day",
            "os_group_by_day",
            "os_version_group_by_day",
            "property_group_by_day",
        ]

        nodes = [
            {
                "name": "fingerprint_property_node",
                "sql": '''%
                    SELECT
                        -- Visits
                        countMerge(review_visits_shown) as user_property_total_reviews_shown,
                        -- Searches
                        countMerge(saved_search_visits) as user_property_total_saved_searches,
                        -- Package/Price
                        countMerge(total_prices) as user_property_total_prices,
                        max(last_price_date) as user_property_last_price_date,
                        argMaxMerge(last_search_type) as user_property_last_search_type,
                        argMaxMerge(last_search_price) as user_property_last_search_price,
                        argMaxMerge(last_search_currency) as user_property_last_search_currency,
                        argMaxMerge(last_search_start_date) as user_property_last_search_start_date,
                        argMaxMerge(last_search_end_date) as user_property_last_search_end_date,
                        argMaxMerge(last_search_adults) as user_property_last_search_adults,
                        argMaxMerge(last_search_children) as user_property_last_search_children,
                        argMaxMerge(last_search_babies) as user_property_last_search_babies,
                        argMaxMerge(last_search_rooms) as user_property_last_search_rooms,
                        argMaxMerge(last_search_status) as user_property_last_search_status,
                        argMaxMerge(last_search_ab_test) as user_property_last_search_ab_test,
                        argMaxMerge(last_search_showed) as user_property_last_search_showed,
                        -- Last visit
                        max(last_visit_date) as user_property_last_visit_date,
                        countMerge(total_visits) as user_property_total_visits,
                        uniqMerge(total_visit_days) as user_property_total_visit_days,
                        max(last_index_date) as user_property_last_index_date,
                        argMaxMerge(last_visit_page_id) as user_property_last_visit_page_id,
                        argMaxMerge(last_visit_page_name) as user_property_last_visit_page_name,
                        argMaxMerge(last_funnel_page_name) as user_property_last_funnel_page_name,
                        argMaxMergeIf(furthest_funnel_page_name, datediff('day', (furthest_funnel_date), now()) <= 30) as user_property_furthest_funnel_page_name,
                        argMaxMerge(last_visit_device) as user_property_last_device,
                        argMaxMerge(last_search_url) as user_property_last_search_url,
                        argMaxMerge(last_visit_referrer) as user_property_last_visit_referrer,
                        -- Bookings
                        countMerge(booking_visits) as user_property_total_bookings,
                        max(last_booking_date) as user_property_last_booking_date,
                        -- Origins
                        max(last_origin_date) as user_property_last_origin_date,
                        toDateTime(topKWeightedMerge(2)(last_origin_dates_uint32)[2]) as user_property_second_to_last_origin_date,
                        argMaxMerge(last_origin_source) as user_property_last_origin_source,
                        argMaxMerge(last_origin_retargeting) as user_property_last_origin_retargeting,
                        argMaxMerge(last_origin_browser) as user_property_last_origin_browser,
                        argMaxMerge(last_origin_browser_major) as user_property_last_origin_browser_major,
                        argMaxMerge(last_origin_browser_version) as user_property_last_origin_browser_version,
                        argMaxMerge(last_origin_os) as user_property_last_origin_os,
                        argMaxMerge(last_origin_os_version) as user_property_last_origin_os_version,
                        argMaxMerge(last_origin_user_agent) as user_property_last_origin_user_agent,
                        argMaxMerge(last_origin_ntw_booked) as user_property_last_origin_ntw_booked,
                        argMaxMerge(last_origin_ntw_visits) as user_property_last_origin_ntw_visits,
                        argMaxMerge(last_origin_ntw_chains) as user_property_last_origin_ntw_chains,
                        argMaxMerge(last_visit_geoname_id) as user_property_last_visit_geoname_id,
                        countMerge(total_origin_search) as user_property_total_origin_search,
                        countMerge(total_origin_facebook) as user_property_total_origin_facebook,
                        countMerge(total_origin_twitter) as user_property_total_origin_twitter,
                        countMerge(total_origin_instagram) as user_property_total_origin_instagram,
                        countMerge(total_origin_kayak) as user_property_total_origin_kayak,
                        countMerge(total_origin_tripadvisor) as user_property_total_origin_tripadvisor,
                        countMerge(total_origin_trivago) as user_property_total_origin_trivago,
                        countMerge(total_origin_direct) as user_property_total_origin_direct,
                        countMerge(total_origin_noorigin) as user_property_total_origin_noorigin,
                        countMerge(total_origin_retargeting) as user_property_total_origin_retargeting,
                        -- tools
                        countMerge(exit_visits_shown) as user_property_total_exits_shown,
                        countMerge(inline_visits_shown) as user_property_total_inlines_shown,
                        countMerge(layer_visits_shown) as user_property_total_layers_shown,
                        countMerge(note_visits_shown) as user_property_total_notes_shown
                    FROM fingerprint_property_grouped c
                    PREWHERE cityHash64({{String(fingerprint, 'aa96f1b6362a46682193c4708cedfaff', required=True)}}, lower({{String(country, 'es', required=True)}}), lower({{String(device, 'desktop', required=True)}}), toUInt128({{UInt128(property_id, '1027947')}})) == c.key'''
            },
            {
                "name": "results",
                "sql": '''%
                    {{max_threads(1)}}
                    SELECT
                        cityHash64({{String(fingerprint, 'aa96f1b6362a46682193c4708cedfaff', required=True)}}, lower({{String(country, 'es', required=True)}}), lower({{String(device, 'desktop', required=True)}}), toUInt128({{UInt128(property_id, '1027947')}})) as key,
                        -- fingerprint_property_node
                        if(user_property_last_origin_date > '1970-01-01 00:00:00', user_property_last_origin_date, null) as user_property_last_origin_date,
                        if(user_property_second_to_last_origin_date > '1970-01-01 00:00:00', user_property_second_to_last_origin_date, null) as user_property_second_to_last_origin_date,
                        user_property_last_origin_source,
                        user_property_last_origin_retargeting,
                        user_property_last_origin_browser,
                        user_property_last_origin_browser_major,
                        user_property_last_origin_browser_version,
                        user_property_last_origin_os,
                        user_property_last_origin_os_version,
                        user_property_last_origin_user_agent,
                        user_property_last_origin_ntw_booked,
                        user_property_last_origin_ntw_visits,
                        user_property_last_origin_ntw_chains,
                        user_property_last_visit_geoname_id,
                        user_property_total_origin_search,
                        user_property_total_origin_facebook,
                        user_property_total_origin_twitter,
                        user_property_total_origin_instagram,
                        user_property_total_origin_kayak,
                        user_property_total_origin_tripadvisor,
                        user_property_total_origin_trivago,
                        user_property_total_origin_direct,
                        user_property_total_origin_noorigin,
                        user_property_total_origin_retargeting,
                        user_property_total_bookings,
                        if(user_property_last_booking_date > '1970-01-01 00:00:00', user_property_last_booking_date, null) as user_property_last_booking_date,
                        user_property_total_exits_shown,
                        user_property_total_inlines_shown,
                        user_property_total_layers_shown,
                        user_property_total_notes_shown,
                        CASE
                            WHEN (user_property_last_origin_source <> 'google' and user_property_last_origin_source <> 'facebook' and user_property_last_origin_source <> 'twitter' and user_property_last_origin_source <> 'instagram' and user_property_last_origin_source <> 'kayak' and user_property_last_origin_source <> 'tripadvisor' and user_property_last_origin_source <> 'trivago' and user_property_last_origin_source <> '') THEN 'direct'
                            WHEN user_property_last_origin_source = 'google' THEN 'search'
                            WHEN user_property_last_origin_source = '' THEN 'noorigin'
                            ELSE user_property_last_origin_source
                        END as user_property_last_origin,
                        user_property_total_reviews_shown,
                        user_property_total_saved_searches,
                        user_property_total_prices,
                        if(user_property_last_price_date > '1970-01-01 00:00:00', user_property_last_price_date, null) as user_property_last_price_date,
                        user_property_last_search_type,
                        user_property_last_search_price,
                        user_property_last_search_currency,
                        if(user_property_last_search_start_date > '1970-01-01', user_property_last_search_start_date, null) as user_property_last_search_start_date,
                        if(user_property_last_search_end_date > '1970-01-01', user_property_last_search_end_date, null) as user_property_last_search_end_date,
                        user_property_last_search_adults,
                        user_property_last_search_children,
                        user_property_last_search_babies,
                        user_property_last_search_rooms,
                        user_property_last_search_status,
                        user_property_last_search_ab_test,
                        user_property_last_search_showed,
                        if(user_property_last_visit_date > '1970-01-01 00:00:00', user_property_last_visit_date, null) as user_property_last_visit_date,
                        user_property_total_visits,
                        user_property_total_visit_days,
                        if(user_property_last_index_date > '1970-01-01 00:00:00', user_property_last_index_date, null) as user_property_last_index_date,
                        user_property_last_visit_page_id,
                        user_property_last_visit_page_name,
                        user_property_last_funnel_page_name,
                        user_property_last_device,
                        user_property_last_search_url,
                        user_property_last_visit_referrer,
                        CASE user_property_last_funnel_page_name
                            WHEN 'Calendar' THEN 2
                            WHEN 'Rooms and Rates' THEN 3
                            WHEN 'Packages' THEN 3
                            WHEN 'User Register Page' THEN 4
                            WHEN 'Booking Confirmed' THEN 5
                            ELSE 0
                        END as user_property_last_funnel_page_code
                    FROM
                        fingerprint_property_node''',
            }
        ]

        pipe_name = 'example'
        token_name = 'example endpoint api'
        u = Users.get_by_id(self.WORKSPACE_ID)
        with User.transaction(u.id) as user:
            for ds_name in datasources:
                user.add_datasource(ds_name)
            pipe = user.add_pipe(pipe_name, nodes=nodes)
            pipe.endpoint = pipe.pipeline.nodes[-1].id
            user.update_pipe(pipe)
            user.add_token(token_name, scopes.PIPES_READ, pipe.id)

        self.u = Users.get_by_id(self.WORKSPACE_ID)
        self.variables = {
            'fingerprint': 'anything'
        }

        self.pipe = self.u.get_pipe(pipe_name)
        self.template_execution_results = {}
        access_info = self.u.get_token_access_info(token_name)
        self.readable_resources = access_info.get_resources_for_scope(scopes.DATASOURCES_READ, scopes.PIPES_READ)

        self.assertEqual(User.replace_executor._max_workers, 1, "This test is designed for 1 worker only")

        await self.replace_tables_with_options(flush=False, randomize=None, sync=False)  # Ensure warmup (for processes)
        await IOLoop.current().run_in_executor(User.replace_executor, get_template_and_variables.cache_clear)
        timings_with_cache = await self.get_replace_timings(flush=False, randomize=None)

        total_cached = sum(timings_with_cache)
        print(f"Total with cache: {total_cached}")
        self.check_timings(timings_with_cache, max_mean=.04, max_p90=.045, max_min=.035)

        timings_without_cache = await self.get_replace_timings(flush=True, randomize=None)

        total_without_cache = sum(timings_without_cache)
        print(f"Total without cache: {total_without_cache}")
        self.check_timings(timings_without_cache, max_mean=.08, max_p90=.9, max_min=.7)

        improvement = total_without_cache / total_cached
        print(f"Improvement: {improvement:.3f}x")
        self.assertGreater(improvement, 1.3, "Timings with cache should be much faster than without it")
