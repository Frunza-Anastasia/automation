FROM jenkins/ssh-agent

RUN apt-get update && apt-get install -y php-cli php-xml php-mbstring git unzip

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer
