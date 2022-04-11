sudo apt update
sudo apt install nodejs npm
sudo curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | sudo bash
sudo source ~/.profile
nvm i 17
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt update
sudo apt install yarn
nvm i -g wappalyzer
mkdir source
cd source
git clone https://github.com/wappalyzer/wappalyzer
cd wappalyzer
yarn install
yarn run link
