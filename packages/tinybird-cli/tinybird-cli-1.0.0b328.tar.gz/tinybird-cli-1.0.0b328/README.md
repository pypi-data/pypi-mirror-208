# What is this?

Tinybird Analytics is a blazing fast analytics engine for your serverless applications.
Think of it as a set of next-generation lego pieces for building data workflows and applications which rely on real-time analytics.

## Developing tinybird.co?

In order to start contributing you'll need to install:
- Some external services needed for analytics (ClickHouse, Varnish, Redis, Kafka, etc)
- This project, which is constitutes the actual development environment


# Installing dependencies and external services

## 1. Checkout this repo

You'll need some of the files in this repo for configuring some of the services.

## 2. Get and configure ClickHouse

### 2.1 Compile or install ClickHouse

>Current productions versions are [23.3.1.2823](https://github.com/ClickHouse/ClickHouse/releases/tag/v23.3.1.2823-lts) and [22.8.11.15](https://github.com/ClickHouse/ClickHouse/releases/tag/v22.8.11.15-lts).


To help you choose the right version of ClickHouse to install, [take a look at this section in the FAQ](#which-clickhouse-version-should-i-install)

There are different alternatives to get ClickHouse:

- **Downloading binaries**
    
    This is the easiest way to have multiple ClickHouse versions locally is to use pre-built binaries. Check out [how to install it from tgz archives](https://clickhouse.com/docs/en/getting-started/install/#from-tgz-archives) and [why you don't need to build ClickHouse](https://clickhouse.tech/docs/en/development/build/#you-dont-have-to-build-clickhouse).
    [This is the current production version for Linux](https://packages.clickhouse.com/tgz/stable/clickhouse-common-static-22.8.11.15-amd64.tgz), while the rest can be found [in the stable dir of the tgz archive](https://packages.clickhouse.com/tgz/stable/).
    
    >For MacOs, you'll need to download the latest version of ClickHouse already compiled by running:
    >```bash
    >curl https://clickhouse.com/ | sh
    >chmod a+x ./clickhouse
    >````
    > 

    You can download the `clickhouse-common-static` tgz for any stable released ClickHouse version. That contains the standalone binaries within its `usr/bin` directory. This way, you can have different portable versions of ClickHouse that you can use to test. Then, you simply set `PATH` env var as explained in the following sections to choose which version to use. e.g. of directory structure:
    
    ```bash
    /home/Tinybird/ch-versions
    ├── 23.3.1.2823/usr/bin/
    │   ├── clickhouse
    │   ├── clickhouse-extract-from-config -> clickhouse
    │   ├── clickhouse-library-bridge
    │   └── clickhouse-odbc-bridge
    ├── 22.8.11.15/usr/bin/
    │   ├── clickhouse
    │   ├── clickhouse-extract-from-config -> clickhouse
    │   ├── clickhouse-library-bridge
    │   └── clickhouse-odbc-bridge
    ```

- **Local Installation on M1 Mac**

    OSX System Integrity will block the standard install procedure recommended in the [https://clickhouse.com/docs/en/install/#self-managed-install](ClickHouse Docs), therefore you must also use the binary-path flag during the install *and all subsequent calls to the clickhouse binary*
    
    ```bash
    curl https://clickhouse.com/ | sh
    sudo ./clickhouse install --binary-path=/usr/local/bin
    ```

- ** Compiling ClickHouse**
You'll need 70 GB of free disk space. It is recommended to use our production version (v22.8.11.15) following its compilation docs: [https://github.com/ClickHouse/ClickHouse/blob/v22.8.11.15-lts/docs/en/development/build.md](https://github.com/ClickHouse/ClickHouse/blob/v22.8.11.15-lts/docs/en/development/build.md). The final binary is generated at `[build_dir]/programs/clickhouse`. You can use this compiled version setting the `PATH` env var accordingly.

### 2.2 Configure your ClickHouse

To configure your ClickHouse instances you need to know several things about production:

* The configuration is generated via ansible.
* All clusters use replication (but not all of them have more than 1 replica)
* The configuration changes based on customer settings and the ClickHouse version.

The CI, which is probably what you are most interested on, does the same thing and generates its config via ansible:
* The one and only source of truth about the configuration is [ci.yaml](./deploy/inventories/ci.yml)
* Currently (2023-04-04) all the CI (and you) need to run the tests are 2 ClickHouse instances.
* Instances are usually called `clickhouse-01` and `clickhouse-02` but the name is meaningless.
* The CI expect you to have 2 clusters: tinybird and tinybird_b available.

You now need to prepare to run two ClickHouse 'Shards' locally - each requires separate data, logs and other directories and config files. For the following instructions, ensure any directory path that defaults to 'clickhouse' actually then points to either 'clickhouse-1' or 'clickhouse-2'.

#### 2.2.1 Get the config files

In order to get some complete configuration files (config.xml and users.xml) there are 2 ways:

**From Gitlab CI:**

Go to any Gitlab CI pipeline. check the ch_config stages and download the artifacts. Beware that CI mixes CH versions, so for example you might get clickhouse-01 config with 22.8 and clickhouse-02 config for 23.3.

**From tests:**
Use the ones stored under test_ch_config/$version. These might not be up to date or available for all releases, so the getting them from the CI itself is preferred.

```bash
sudo cp -r test_ch_config/23.3/* /etc
```

Whichever method you choose to get the config files, you might need to change their ownership under `/etc` to avoid problems when running ClickHouse.

Outside the regular superuser bash (so you can set ownership to your regular user), run:

```bash
sudo chown -R %(whoami):$(id -gn) /etc/clickhouse-server*
```

#### 2.2.2 Update /etc/hosts

```bash
sudo su
echo '127.0.0.1 redis clickhouse-01 clickhouse-02 zookeeper' >> /etc/hosts
```

#### 2.2.3 Path configuration

You have two options to correctly set the paths:

- Leave the CI paths that you'll find in the config files (`/builds/tinybird/analytics/ch-${replica_num}`) and create those dirs locally):
    ```bash
    sudo mkdir -p /builds/tinybird/analytics/ch-1/ /builds/tinybird/analytics/ch-2/ /builds/tinybird/analytics/clickhouse_logs_1/ /builds/tinybird/analytics/clickhouse_logs_2/
    sudo chown $(whoami) /builds/tinybird/analytics/
    ```
    
- Change them to whatever location you prefer, and update them in /etc/clickhouse-server-1/config.xml` and `/etc/clickhouse-server-2/config.xml` (changes required under `LOGGING` and `PATHS`)

#### 2.2.4 Ports configuration

Port numbers do not matter (you can use any), but there **must** be 877 difference (9000-8123) between the HTTP and TCP ports. This is due to a limitation in the app logic that will be removed in the future.

The HTTP ports must later be passed to the Varnish config, and that's what the application will use. You can define some variables for simplicity and use them in the config files:

```bash
export CH_PORT_01=28123 CH_PORT_02=38123 CH_LB_HOST=ci_ch CH_LB_PORT=6081
```

**Mac only**

For Mac you need to configure the TCP port to 9001 due to a bug in clickhouse-local that limits connections to the default port. You'll need to change both config files in a couple of places:

- Connections (different values per instance):

    clickhouse-server-1/config.xml:
    
    ```xml
    <!-- ################ CONNECTIONS ################ -->
        <http_port from_env="CH_PORT_01" />
        <tcp_port>9000</tcp_port>
        <interserver_http_host>clickhouse-01</interserver_http_host>
        <interserver_http_port>9009</interserver_http_port>
    ```

    clickhouse-server-2/config.xml:
    
    ```xml
    <!-- ################ CONNECTIONS ################ -->
        <http_port from_env="CH_PORT_01" />
        <tcp_port>9001</tcp_port>
        <interserver_http_host>clickhouse-02</interserver_http_host>
        <interserver_http_port>9010</interserver_http_port>
    ```

- Remote servers (same changes in both files):
    ```xml
    <!-- ################ REPLICATION / ZOOKEEPER ################ -->
    
    <!--(...) -->
    
    <remote_servers>
    <tinybird>
        <shard>
            <internal_replication>true</internal_replication>
            <replica>
                <host>clickhouse-01</host>
                <port>9000</port>
            </replica>
            <replica>
                <host>clickhouse-02</host>
                <port>9001</port>
            </replica>
        </shard>
    </tinybird>
    <tinybird_b>
        <shard>
            <internal_replication>true</internal_replication>
            <replica>
                <host>clickhouse-01</host>
                <port>9000</port>
            </replica>
            <replica>
                <host>clickhouse-02</host>
                <port>9001</port>
            </replica>
        </shard>
    </tinybird_b>
    </remote_servers>
    ```

### 2.3 Start ClickHouse with Default single version

```bash
clickhouse server --config-file=/etc/clickhouse-server-1/config.xml
clickhouse server --config-file=/etc/clickhouse-server-2/config.xml
```

To change to a different ClickHouse version use a different binary, for example:

```bash
/home/Tinybird/ch-versions/22.8.11.15/usr/bin/clickhouse server --config-file=/etc/clickhouse-server-1/config.xml
```


One good way to make things easier for you would be to use shell aliases instead:

```bash
alias ch_server-01='clickhouse server --config-file=/etc/clickhouse-server-1/config.xml'
alias ch_server-02='clickhouse server --config-file=/etc/clickhouse-server-2/config.xml'
```


### 2.4 Access and test that ClickHouse has started correctly

You should have at least 2 ClickHouse instances:

**Linux (default ports):**
* clickhouse-01:29000
* clickhouse-02:39000

**Mac (the ones you put in the config files):**
* clickhouse-01:9000
* clickhouse-02:9001

To access them you should use the `-h` and `--port` options of the ClickHouse client. For example in Linux:

```
$ clickhouse client -h clickhouse-01 --port 29000
ClickHouse client version 23.3.1.2537.
Connecting to clickhouse-01:49000 as user default.
Connected to ClickHouse server version 23.3.1 revision 54462.

Warnings:
 * Linux transparent hugepages are set to "always". Check /sys/kernel/mm/transparent_hugepage/enabled

production-01 :)
```

One simple way to avoid needing to write host or port numbers is to use shell aliases:

**Linux:**
```bash
alias ch_client_prod-01='clickhouse client -h clickhouse-01 --port 29000'
alias ch_client_prod-02='clickhouse client -h clickhouse-02 --port 39000'
```

**Mac:**

```bash
alias ch_client_prod-01='clickhouse client -h clickhouse-01 --port 9000'
alias ch_client_prod-02='clickhouse client -h clickhouse-02 --port 9001'
```

Then you can run the client simply with:
```bash
$ ch_client_prod-01 --query "Select 1"
1
```

You can check if your clusters are correctly configured from the ClickHouse console:

```sql
:) select cluster, shard_num, replica_num, host_name, host_address, port, is_local from system.clusters

┌─cluster────┬─shard_num─┬─replica_num─┬─host_name─────┬─host_address─┬──port─┬─is_local─┐
│ tinybird   │         1 │           1 │ clickhouse-01 │ 127.0.0.1    │ 49000 │        1 │
│ tinybird   │         1 │           2 │ clickhouse-02 │ 127.0.0.1    │ 59000 │        0 │
│ tinybird_b │         1 │           1 │ clickhouse-01 │ 127.0.0.1    │ 49000 │        1 │
│ tinybird_b │         1 │           2 │ clickhouse-02 │ 127.0.0.1    │ 59000 │        0 │
└────────────┴───────────┴─────────────┴───────────────┴──────────────┴───────┴──────────┘
```


## 3. Install Varnish as the ClickHouse LB
### 3.1 Install

* On Linux

    ```bash
    sudo apt install varnish
    ```

* On macOS:

    ```bash
    brew install varnish
    ```

### 3.2 Generate a configuration

Use the values from your ClickHouse installation/configuration:

```bash
export CH_PORT_01=28123 CH_PORT_02=38123 CH_LB_HOST=ci_ch CH_LB_PORT=6081 # Skip it if you already set them when configuring ClickHouse
python3.11 gitlab/prepare_varnish_db_ci_config.py ${CH_LB_HOST} ${CH_LB_PORT} 127.0.0.1 ${CH_PORT_01} 127.0.0.1 ${CH_PORT_02} > ch_lb.vcl
```

### 3.3 Update /etc/hosts

Your system must be able to resolve the CH_LB_HOST host, you can add it to your hosts files with something like:

```bash
echo "127.0.0.1 ${CH_LB_HOST}" | sudo tee -a /etc/hosts
```

### 3.4 Run Varnish

* In the foreground

  >:warning: This is the only option for Mac systems if varnish was installed through `brew`

    ```bash
    varnishd -a :${CH_LB_PORT} -T 127.0.0.1:6082 -f $(pwd)/ch_lb.vcl -s malloc,32m -F -p max_retries=1
    ```

* As a service (Linux only)

  For systemd, you can [use and adapt the template from our own Varnish unit file](https://gitlab.com/tinybird/analytics/-/blob/master/deploy/roles/ansible-varnish/templates/varnish.service.j2).

Once the ClickHouse load balancer is running, you can change the database_server in your workspaces to be "http://ci_ch:6081".

To check that varnish and ClickHouse are well configured together, start both and run:

```bash
curl ci_ch:6081
```

#### Check logs

You can verify what is happening with Varnish using `varnishlog`:

```bash
sudo varnishlog
```

## 4. Install and configure Redis

### On Linux:

```bash
sudo apt install redis-server
```

and then the redis-cell extension using the file from this repo:

```bash
sudo cp deploy/files/redis-cell/redis-cell-v0.2.5-x86_64-unknown-linux-gnu/libredis_cell.so /var/lib/redis
echo 'loadmodule /var/lib/redis/libredis_cell.so' | sudo tee -a /etc/redis/redis.conf
```

**Important note:** You need to modify `/etc/redis/redis.conf` and change line `supervised no` to `supervised systemd`.

Lastly, start the service with `sudo systemctl restart redis`. You can also enable it to be automatically started on boot: `sudo systemctl enable redis`. You can check that it is running by executing `redis-cli ping`.


### On Mac:

```bash
brew install redis
```

For installing the redis-cell extension from this repo. Choose the file according to your Mac's architecture:

  
* With M1
    ```bash
    sudo cp deploy/files/redis-cell/redis-cell-v0.2.5-aarch64-apple-darwin/libredis_cell.dylib /opt/homebrew/etc/
    echo 'loadmodule /opt/homebrew/etc/libredis_cell.dylib' | sudo tee -a /opt/homebrew/etc/redis.conf
    ```

* With Intel
    ```bash
    sudo cp deploy/files/redis-cell/redis-cell-v0.2.5-x86_64-apple-darwin/libredis_cell.dylib /opt/homebrew/etc/
    echo 'loadmodule /opt/homebrew/etc/libredis_cell.dylib' | sudo tee -a /opt/homebrew/etc/redis.conf
    ```

## 5. Install Zookeeper

### On Linux:

```bash
sudo apt install zookeeperd
```

### On Mac:

```bash
brew install zookeeper
```

For better **ZooKeeper performance on macOS**, the recommended JDK/JRE version is Java 8 (instead of the version included with brew's zookeeper). You should be able to keep using your ZooKeeper's Homebrew service by setting the `JAVA_HOME` environment variable so the service picks your own Java installation instead of the one from Homebrew.
You can achieve that in different ways, either modifying the Homebrew's zkServer script (you can find it with `brew info zookeeper`) or by using `launchctl setenv JAVA_HOME $JAVA_HOME` in your shell rc script.

The version you'll need depends on the type of Mac:

* With Intel:

    Although you can use the Oracle's Java 8, [we found](https://3.basecamp.com/4360466/buckets/18798855/messages/5468220651) that performance with it doesn't improve that much. A better alternative seems to be using [Adoptium's JDK](https://adoptium.net/temurin/releases/?version=8), downloading the binaries or with brew. 
    
    Just remember to set the `JAVA_HOME` env var:

    ```bash
    brew tap homebrew/cask-versions
    brew install --cask temurin8
    
    # add the following 2 lines to your shell rc file:
    export JAVA_HOME=""/Library/Java/JavaVirtualMachines/temurin-8.jdk/Contents/Home""
    launchctl setenv JAVA_HOME $JAVA_HOME
    ```

* With M1

    For M1 you can install Adoptium's version as explained above, or you can install one specifically compiled for M1. There's no much difference in performance, if any zulu's version sometimes performed slightly better but not very significantly better:
    
    ```bash
    brew tap homebrew/cask-versions
    brew install --cask zulu8
    
    # add the following 2 lines to your shell rc file:
    export JAVA_HOME="/Library/Java/JavaVirtualMachines/zulu-8.jdk/Contents/Home"
    launchctl setenv JAVA_HOME $JAVA_HOME
    ```

## 6. Extra system-wide configuration

### On Linux

Increase the max number of opened files:

```bash
ulimit -n 8096
```

To make that change persistent, you will need to add to your `/etc/security/limits.conf` the following:

```bash
# Increase # of file descriptors
*               hard    nofile          8096
*               soft    nofile          8096
```

### On Mac

You may have noticed that ClickHouse takes at least 5 seconds to do some operations. For instance, if you execute ClickHouse Local with a simple query, it may take more time than expected:

```bash
time ./clickhouse local --query 'Select 1'
1
./clickhouse local --query 'Select 1'  0.06s user 0.02s system 1% cpu 5.092 total
```

This problem is related to how macOS [manages internally the DNS queries and the hostname](https://stackoverflow.com/questions/44760633/mac-os-x-slow-connections-mdns-4-5-seconds-bonjour-slow)

To fix this, you need to add your laptop hostname to the `/etc/hosts` file. For example doing:

```bash
sudo su
echo 127.0.0.1 localhost $(hostname) >> /etc/hosts
```

This should be enough to fix the problem.

### On both platforms

It is necessary to have `clickhouse` in your `$PATH` when running the application.
You can set it up in your environment by altering the variable on your session or by
adding it to your shell init scripts (likely `~/.bashrc` or `~/.zshrc`).
This will be an example for a self-compiled installation:

```bash
export PATH=$PATH:/usr/local/bin/
```

## 7. Install Kafka [optional]

### On Linux

Download Kafka:

```bash
curl 'https://archive.apache.org/dist/kafka/2.8.0/kafka_2.13-2.8.0.tgz' | tar xz
```

To avoid having to setup the KAFKA_PATH envvar, decompress it on the parent folder of analytics:

```bash
my/dir/analytics
my/dir/kafka_2.13-2.8.0
```

### On Mac
```bash
brew install kafka
```

## 8. Start dependency services

### On Linux:
Leave open the zookeeper service:

```bash
sudo /usr/share/zookeeper/bin/zkServer.sh start-foreground
```

### On Mac M1

Your services, apart from ClickHouse, should all be in `brew services`, therefore you can start them all with brew commands.

```bash
brew services list
# Name      Status User File
# kafka     none
# redis     none
# varnish   none
# zookeeper none

brew services start --all
#==> Successfully started `kafka` (label: homebrew.mxcl.kafka)
#==> Successfully started `redis` (label: homebrew.mxcl.redis)
#==> Successfully started `varnish` (label: homebrew.mxcl.varnish)
#==> Successfully started `zookeeper` (label: homebrew.mxcl.zookeeper)
```

> :information: Most likely you'll need to start varnish manually as described in [the varnish section](#34-run-varnish) instead of as brew service.

# Installing analytics

## 1. Install Python >= 3.11.2

### On Linux

```bash
wget -qO - https://packages.confluent.io/deb/7.3/archive.key | sudo apt-key add -
sudo add-apt-repository "deb https://packages.confluent.io/clients/deb $(lsb_release -cs) main"
sudo apt install python3-pip libcurl4-openssl-dev libsqlite3-dev liblzma-dev libssl-dev libbz2-dev libffi-dev librdkafka1
```

Install pyenv to use the recommended python version (3.11.2), following [pyenv's installation guide](https://github.com/pyenv/pyenv-installer)

Then install python 3.11.2 and set it as the default for our analytics directory:

```bash
# 'analytics' here is the path of this cloned repo
cd analytics/
CONFIGURE_OPTS=--enable-shared pyenv install 3.11.2
pyenv local 3.11.2
```

### On Mac

Install [pyenv's system dependencies](https://github.com/pyenv/pyenv/wiki#troubleshooting--faq):

If you haven't done so, install Xcode Command Line Tools (xcode-select --install) and Homebrew. Then:

```bash
brew install readline sqlite3 xz zlib
```

Install pyenv, following [pyenv's installation guide](https://github.com/pyenv/pyenv-installer)

Install Python >= 3.11.2:

```bash
pyenv install 3.11.2
```

Set it as a global version if you want to always use this one:

```bash
pyenv global 3.11.2
```

## 2. Create your venv and install all dependencies:

### On Linux

```bash
sudo apt install libsnappy-dev

pyenv exec python3 -m venv .e

# WARNING! Version 23.1 might fail during the final install, skip this upgrade if that happens
.e/bin/python3 -m pip install --upgrade pip
. .e/bin/activate

pip install wheel==0.40.0

PYCURL_SSL_LIBRARY=openssl pip install --editable .
```

(`--editable` option means you can change code inside tinybird folder). Note that you need, at least, ClickHouse headers in order to install python dependencies

- virtualenv alternative in case something goes wrong with pyenv:

    ```bash
    sudo apt-get install python3-dev
    pip3 install virtualenv
    virtualenv -p python3.11 .e
    . .e/bin/activate
    ```

- In case you have problems installing `confluent-kafka`, compile `librdkafka` and retry:

    ```bash
    git clone https://github.com/edenhill/librdkafka.git --depth=1 --branch=v1.9.2
    cd librdkafka
    ./configure --prefix=/usr
    make -j$(nproc) && sudo make install
    ```

### On Mac:

* With M1

    ```bash
    brew install openssl@1.1 curl libffi librdkafka postgresql@13 snappy
  
    python3 -m venv .e
    . .e/bin/activate

    # Needs the latest pip version to correctly install clickhouse-toolset
    # WARNING! Version 23.1 might fail during the final install, skip this upgrade if that happens
    pip install --upgrade pip

    # Uninstall pycurl in case you have a stale version
    pip uninstall -y pycurl

    # cffi needs to be installed separately because with the --editable option it fails
    pip install cffi==1.14.5 grpcio
  
    export PYCURL_SSL_LIBRARY=openssl 
    export LDFLAGS="-L$(brew --prefix openssl@1.1)/lib -L$(brew --prefix curl)/lib -L$(brew --prefix librdkafka)/lib"
    export CPPFLAGS="-I$(brew --prefix openssl@1.1)/include -I$(brew --prefix snappy)/include -I$(brew --prefix curl)/include -I$(brew --prefix librdkafka)/include"

    # After this, check if pycurl is correctly installed and configured by executing "python -c 'import pycurl'", 
    # which must return nothing. If it fails, run `brew link curl --force`, uninstall pycurl and install again.
    pip install --no-cache-dir --compile --config-settings="--openssl-dir=$(brew --prefix openssl@1.1)" pycurl==7.45.1

    export CFLAGS="-I$HOMEBREW_PREFIX/include"
    pip install --editable .
    ```

* With Intel

    ```bash
    brew install openssl@1.1 curl libffi librdkafka postgresql@13 snappy
    python3 -mvenv .e
    . .e/bin/activate

    # Needs the latest pip version to correctly install clickhouse-toolset
    # WARNING! Version 23.1 might fail during the final install, skip this upgrade if that happens
    pip install --upgrade pip
  
    # Install pycurl with the correct openssl files. 
    export PYCURL_SSL_LIBRARY=openssl
    export LDFLAGS="-L$(brew --prefix openssl@1.1)/lib -L$(brew --prefix curl)/lib -L$(brew --prefix librdkafka)/lib" 
    export CPPFLAGS="-I$(brew --prefix openssl@1.1)/include -I$(brew --prefix snappy)/include -I$(brew --prefix curl)/include -I$(brew --prefix librdkafka)/include"

    # After this, check if pycurl is correctly installed and configured by executing "python -c 'import pycurl'", 
    # which must return nothing. If it fails, run `brew link curl --force`, uninstall pycurl and install again.
    pip install pycurl==7.45.1 --compile --no-cache-dir

    # Finally install the rest of dependencies.
    pip install --editable .
    ```

## 3. Config pre-commit to install a pre-commit hook to prevent lint errors:

```bash
pre-commit install
```

## 4. Run the server

You need to set the $PATH correctly with the CH version you want to use in the app, for example:

```bash
PATH=$PATH:/home/Tinybird/ch-versions/22.8.11.15/usr/bin tinybird_server --port 8001
```

> Note: If you are using VSCode or Pycharm or some other IDE you may want to set tinybird.app up as a Run configuration

```bash
tinybird_server --port 8001
```

**Important note:** on macOS add `OBJC_DISABLE_INITIALIZE_FORK_SAFETY` as follows

```bash
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES tinybird_server --port 8001
```

To stop the server and kill the running process, we suggest adding the following aliases:

```sh
alias tinybird_stop="ps -ef | grep 'tinybird_server' | grep -v grep | awk '{print $2}' | xargs kill -9"
alias tinybird_stop_python="ps -ef | grep 'analytics/.e/bin/python' | grep -v grep | awk '{print $2}' | xargs kill -9"
```

To start HFI server:
```bash
uvicorn tinybird.hfi.hfi:app --port 8042
```

## 4. Test code locally

### 4.1 Install testing dependencies

    ```bash
    pip install -e ".[test]"
    ```

### 4.2 Run the tests with [pytest](https://docs.pytest.org/en/stable/usage.html):

There are different options for running tests:

* Run all tests

   ```bash
   # Note that this is very intensive and not a good test for 'is my new install working'
   pytest tests
   ```

* Run all tests in a single file:

   ```bash
   pytest tests/views/test_api_datasources.py -vv
   ```

* Run a single test:

   ```bash
   pytest tests/views/test_api_datasources.py -k test_name
   ```
  
### 4.3 Tips and handy tools
 
When trying to fix flaky tests, sometimes the problem can be difficult to reproduce locally. For those cases you can use flakefinder:

```bash
pip install pytest-xdist
pip install pytest-flakefinder
```

Then you only need to pass the flag `--flake-finder` to the call. This will run every test 50 times (default). Every test is run independently and you can even use xdist to send tests to multiple processes. You can check available options (like number of runs or timeout values) [in the GH page](https://github.com/dropbox/pytest-flakefinder).

## 5. Install the UI

We encourage you to use **node** version 16 to have the same version that we use in production builds. Then, in the root of the project:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
nvm install 16
nvm use 16
```

Make sure your npm version is the latest available or at least a version >= 9. To update it you can use
```bash
 npm install -g npm@latest
```

Once Node is installed, install pnpm version 7.X using:
```bash
npm install -g pnpm@7.30.5
```

Once Node, npm and pnpm are installed, run the setup in the code directory

```bash
pnpm run setup
```

You can now use the UI by opening `localhost:8001` in your browser.

If you want to make changes and check how they look:

```bash
pnpm run dev:watch
```

Don't forget to test your changes:

```bash
pnpm run test
```

Or test + watch 🤗:

```bash
pnpm run test:watch
```

If you want to clean your environment:

```bash
pnpm run clean
```

You have more information about development [here](development.md).

## 6. Running development instance of CLI

You can point Tinybird's CLI to any host you want, as long as you have the proper auth token for it.

When installing this project you get a development version of the CLI, so in your venv you can just run:

```bash
tb auth --host [HOST] --token [ADMIN TOKEN]
```

and that will run the development instance you just installed against the host you chose.

### Run development CLI against local server

You first need to get an admin token for your local application. This can only be done through the UI so you need to [install the UI](#5-install-the-ui) locally first, and then get a token as usual.

Once you have the admin token, simply run (assuming you're running the local server on the port 8001):

```bash
tb auth --host localhost:8001 --token [ADMIN TOKEN]
```


## Extra notes

### Useful commands

If running CH with docker, you can do the following to connect to ClickHouse client

```bash
docker exec -it tt ClickHouse client
```

### Configuring the metrics

If you've configured your ClickHouse environment following the *advanced* steps, you should be able to activate the metrics by changing the `default_secrets.py` file adding: `metrics_cluster="metrics"`


# FAQ

## Which ClickHouse version should I install?

That depends on your role. As a rule of thumb:

* If you are not a developer or don't want to do backend-related work. Download the recommended prebuilt release.

* If you are doing backend work, you should have available several different releases available for testing.
  See the official [prebuilt binaries](https://clickhouse.com/docs/en/getting-started/install/#from-tgz-archives).
  You should also have your own build copy of ClickHouse for testing and debugging purposes as explained [here](#installing-the-development-environment)

Finally, ClickHouse/master should be considered to be stable and fully compatible with Analytics. All tests should pass and everything work as expected.
If you detect any issue, please open a ticket and tag it as `ClickHouse Team`

## What do I do to validate my development environment is working correctly?

Browse to [http://localhost:8001/dashboard](http://localhost:8001/dashboard). You'll be prompted to login with your gmail account. Go back to /dashboard once you do and try importing

## I can't connect to ClickHouse with tinybird configuration

```bash
clickhouse client -h clickhouse-01 --port 29000
```

## Where is the marketing website code?

It is in [webflow](https://webflow.com/)

## Where is the blog hosted?

It is generated with Jekyll, and it is located in other [repository](https://gitlab.com/tinybird/blog).

## How can I see the documentation?

There is an automatic deploy job created so every time you merge something in master, if everything goes OK, the latest version of the documentation will be available at [https://docs.tinybird.co](https://docs.tinybird.co)


## Debugging problems in gitlab CI

You can use `gitlab-runner` to execute any `.gitlab-ci.yml` job locally. Follow these steps to debug any of those jobs:

* Modify the `.gitlab-ci.yml` file, including `tail -f /dev/null` in the script section of the job
* Run the job you need with gitlab-runner, for instance: `gitlab-runner exec docker tests_integration_ch_207_py38`
* Wait until the container stops in `tail -f /dev/null`
* `docker ps` to list the name of the Docker container
* Open a shell session inside the container `docker exec -it <docker_name_from_previous_step> /bin/bash`
* Now you can run anything you need to debug, including breakpoints with pdb, etc.
* Once you finish stop the container `docker stop <docker_name>`

Note: If you do any modification to a project file, you need to commit it in order to be available in the Docker container. Once you finish you can squash all the commits.

## Adding distributed metrics

Read the [metrics](METRICS.md) guide.

# Changelog

We have a `CHANGELOG.md` file in the root of the project to document notable changes.

This file uses the `union` git merge strategy to avoid conflicts by taking all available options when some conflict happens. To add a new entry to the changelog and avoid duplicates and bad formatting, you need to take into account the following:

* Maintain the branch up to date with master so you can use the latest version of the changelog.
* There should be one entry in the changelog for each week. If the current week is not present, it should be added. Take into account that the changelog is ordered by date, so the latest entry should be at the top. This can lead to duplicates if someone else has added an entry for the current week. Be sure to check the last changes in master branch.
* Avoid reordering the changelog entries. If someone else updates the same lines, it will lead to duplicates and strange formatting. We should follow the next order: `Added`, `Changed`, `Deprecated`, `Fixed`, `Released`, `Removed`, `Security`.
* The changelog should be written in a way that it can be understood by a non-technical person.
* With every MR, a job will trigger to check if the changelog was updated. If it is not the case, the job will fail. There are a couple of exceptions to avoid this by adding the label `[changelog_not_needed]`:
  - The issue is not product related, but it is a pure engineering task.
  - The incoming code is under a feature flag and is not visible to the users.
