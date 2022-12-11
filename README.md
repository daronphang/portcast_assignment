# Portcast Assignment

Project is used to run a basic Flask app with MySQL as DB using docker-compose.

## Getting Started

All steps are configured for Linux as I will be using it for the project.

**If you encounter permissions error, use sudo for commands.**

**Step 1:** Make sure git is installed on your host machine.

```console
$ sudo apt-get update && \
sudo apt install git-all
$ git version
```

**Step 2:** Clone the project into your local machine (specify your directory).

```console
$ cd /home/daronphang/path/to/project
$ git clone
```

**Step 3:** Setup your environment variables. Create two files called '.env' and 'test.env', and place them into the parent directory you have cloned in i.e. '/portcast_app'.

#### Development Env

```env
MYSQLHOST=mysqldb
MYSQLUSERNAME=root
MYSQLPASSWORD=portcast_is_awesome
MYSQLPORT=3306
MYSQLDATABASE=portcast_assignment
```

#### Test Env

```env
TESTMYSQLHOST=localhost
TESTMYSQLUSERNAME=root
TESTMYSQLPASSWORD=portcast_is_awesome
TESTMYSQLPORT=6033
TESTMYSQLDATABASE=testing_database
```

## Prerequisites

### 1. Python3

**Step 1:** Install latest Python from official repository.

https://www.python.org/

**Step 2:** Verify Python is installed.

```console
$ python --version
```

### 2. Docker

**Step 1:** Make sure Docker is installed on host machine.

https://docs.docker.com/engine/install/ubuntu/

**Do not install Docker via snap as AppArmour will interfere with networking. Follow the installation steps provided by official Docker website for your distribution.**

```console
$ sudo snap list
$ sudo snap remove docker --purge
```

## Running

**Step 1:** Change to the directory where your project was cloned.

```console
$ cd /home/daronphang/path/to/project
```

**Step 2:** Start application with docker-compose.

```console
$ docker compose up -d
```

**Step 3:** Configure database by going into the database container's bash terminal (**first-time setup only**). Container name is mysqldb (specified in docker-compose).

To log into MySQL, use the password specified in the docker-compose file.

```console
$ docker exec -it <DATABASE CONTAINER NAME> bash
$ mysql -u root -p
```

Create database and tables required for application.

```console
$ mysql> CREATE DATABASE portcast_assignment;
$ mysql> USE portcast_assignment;
$ mysql> CREATE TABLE IF NOT EXISTS metaphorpsum_paragraphs (
    uid CHAR(32) PRIMARY KEY NOT NULL,
    paragraph TEXT NOT NULL,
    created_timestamp TIMESTAMP NOT NULL DEFAULT NOW()
);
$ mysql> CREATE TABLE IF NOT EXISTS metaphorpsum_unique_keywords (
    uid INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    keyword VARCHAR(255) NOT NULL,
    paragraph_uid CHAR(32) NOT NULL,
    FOREIGN KEY (paragraph_uid) REFERENCES metaphorpsum_paragraphs(uid),
    created_timestamp TIMESTAMP NOT NULL DEFAULT NOW()
);
```

**Step 4:** You can stop application gracefully with storage persisted in Docker volume.

```console
$ docker compose down
```

## Testing

**Step 1:** Make sure the database container 'mysqldb' is running.

```console
$ docker container ls
$ docker compose up -d  # if database container is not running
```

**Step 2:** cd to the directory of project folder.

```console
$ cd /home/daronphang/path/to/project
```

**Step 3:** Run pytest in terminal.

```console
$ pytest
```
