#!/bin/bash

echo -e "\n  > Starting install..."


# verifying sudo
sudo true

echo -n "  > Updating packages... "
sudo yum update -y &> /dev/null
echo done

# start in home
cd ~
path=".docker-dash-agent"


# checking if dir exists
if [ -d "$path/" ]; then
    # prompting yes or no for overwrite
    while true; do
        read -p "Directory \"$path/\" already exists, overwrite? (y/n) " yn
        case $yn in 
        [yY] ) 
            break
            ;;
        [nN] ) 
            echo "  > Exiting..."; exit
            ;;
        * ) 
            echo invalid response
            ;;
        esac
    done
fi


# downloading github repo
echo -n "  > Downloading repository... "
curl -sSLo ./repo.tar https://api.github.com/repos/JaydenPahukula/docker-dash-grafana-plugin/tarball
echo done

# extracting tar archive
echo -n "  > Extracting agent... "
sudo rm -rf "$path-tmp/" &> /dev/null
mkdir "$path-tmp/" &> /dev/null
tar -sxf ./repo.tar -C $path-tmp/ --strip-components=1 &> /dev/null
sudo rm repo.tar
# extracting agent from repo
sudo rm -rf "$path/"
mv ./$path-tmp/agent $path/
sudo rm -rf "$path-tmp"
echo done

# verifying python
echo -n "  > Verifying python... "
if [ "$(python3.9 --version 2>&1)" != "Python 3.9.16" ]; then
    echo "not found"
    # prompting yes or no for python installation
    while true; do
        read -p "Do you want to install Python 3.9.16? (y/n) " yn
        case $yn in 
        [yY] ) 
            break
            ;;
        [nN] ) 
            echo Exiting...; exit
            ;;
        * ) 
            echo invalid response
            ;;
        esac
    done

    # installing python
    echo -n "  > Installing python (this may take a few minutes)... "
    sudo yum install -y make gcc openssl-devel bzip2-devel libffi-devel zlib-devel &> /dev/null
    curl -sOL https://www.python.org/ftp/python/3.9.16/Python-3.9.16.tgz &> /dev/null
    tar -xzf Python-3.9.16.tgz &> /dev/null
    cd Python-3.9.16 
    sudo ./configure --enable-optimizations &> /dev/null
    sudo make altinstall &> /dev/null
    cd ..
    sudo rm Python-3.9.16.tgz
    sudo rm -rf Python-3.9.16
fi
echo done

# installing and configing systemd
echo -n "  > Configuring systemd... "
sudo yum install -y systemd &> /dev/null
echo done

# configuring service
echo -n "  > Configuring agent service... "
sudo rm /etc/systemd/system/docker-dash-agent.service &> /dev/null
sudo tee -a /etc/systemd/system/docker-dash-agent.service > /dev/null <<- END
    [Unit]
    Description=Docker dash grafana agent
    After=multi-user.target
    
    [Service]
    Type=simple
    Restart=always
    ExecStart=/home/$USER/$path/.venv/bin/python /home/$USER/$path/main.py -p 5050
    
    [Install]
    WantedBy=multi-user.target
END
sudo systemctl daemon-reload
sudo systemctl enable docker-dash-agent.service &> /dev/null
sudo systemctl start docker-dash-agent.service &> /dev/null
echo done

echo ""
echo "Completed installation!"
echo -e "Run \"systemctl status docker-dash-agent.service\" to verify the agent is running"