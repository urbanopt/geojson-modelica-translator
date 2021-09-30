FROM michaelwetter/ubuntu-1804_jmodelica_trunk:latest AS base
USER root

MAINTAINER Nicholas Long nicholas.long@nrel.gov

# Set the version of OpenStudio when building the container. For example `docker build --build-arg
ARG OPENSTUDIO_VERSION=3.2.1
ARG OPENSTUDIO_VERSION_EXT=""
ARG OPENSTUDIO_DOWNLOAD_URL=https://openstudio-builds.s3.amazonaws.com/3.2.1/OpenStudio-3.2.1%2Bbdbdbc9da6-Ubuntu-18.04.deb

ENV OS_BUNDLER_VERSION=2.1.4
ENV RUBY_VERSION=2.7.2
ENV BUNDLE_WITHOUT=native_ext
# Install gdebi, then download and install OpenStudio, then clean up.
# gdebi handles the installation of OpenStudio's dependencies

# install locales and set to en_US.UTF-8. This is needed for running the CLI on some machines
# such as singularity.
RUN apt-get update && apt-get install -y \
        curl \
        vim \
        gdebi-core \
        libsqlite3-dev \
        libssl-dev \
        libffi-dev \
        build-essential \
        zlib1g-dev \
        vim \
        git \
        locales \
        sudo \
    && echo "OpenStudio Package Download URL is ${OPENSTUDIO_DOWNLOAD_URL}" \
    && curl -SLO $OPENSTUDIO_DOWNLOAD_URL \
    && OPENSTUDIO_DOWNLOAD_FILENAME=$(ls *.deb) \
    # Verify that the download was successful (not access denied XML from s3)
    && grep -v -q "<Code>AccessDenied</Code>" ${OPENSTUDIO_DOWNLOAD_FILENAME} \
    && gdebi -n $OPENSTUDIO_DOWNLOAD_FILENAME
    # Cleanup
    RUN rm -f $OPENSTUDIO_DOWNLOAD_FILENAME \
    && rm -rf /var/lib/apt/lists/* \
    && locale-gen en_US en_US.UTF-8 \
    && dpkg-reconfigure locales


RUN curl -SLO https://cache.ruby-lang.org/pub/ruby/2.7/ruby-2.7.2.tar.gz \
    && tar -xvzf ruby-2.7.2.tar.gz \
    && cd ruby-2.7.2 \
    && ./configure \
    && make && make install


## Add RUBYLIB link for openstudio.rb
ENV RUBYLIB=/usr/local/openstudio-${OPENSTUDIO_VERSION}${OPENSTUDIO_VERSION_EXT}/Ruby
ENV ENERGYPLUS_EXE_PATH=/usr/local/openstudio-${OPENSTUDIO_VERSION}${OPENSTUDIO_VERSION_EXT}/EnergyPlus/energyplus

# The OpenStudio Gemfile contains a fixed bundler version, so you have to install and run specific to that version
RUN gem install bundler -v $OS_BUNDLER_VERSION && \
    mkdir /var/oscli && \
    ls /usr/local && \
    cp /usr/local/openstudio-${OPENSTUDIO_VERSION}${OPENSTUDIO_VERSION_EXT}/Ruby/Gemfile /var/oscli/ && \
    cp /usr/local/openstudio-${OPENSTUDIO_VERSION}${OPENSTUDIO_VERSION_EXT}/Ruby/Gemfile.lock /var/oscli/ && \
    cp /usr/local/openstudio-${OPENSTUDIO_VERSION}${OPENSTUDIO_VERSION_EXT}/Ruby/openstudio-gems.gemspec /var/oscli/
WORKDIR /var/oscli
RUN bundle -v
RUN bundle _${OS_BUNDLER_VERSION}_ install --path=gems --without=native_ext --jobs=4 --retry=3

# Configure the bootdir & confirm that openstudio is able to load the bundled gem set in /var/gemdata
VOLUME /var/simdata/openstudio
WORKDIR /var/simdata/openstudio
RUN openstudio --verbose --bundle /var/oscli/Gemfile --bundle_path /var/oscli/gems --bundle_without native_ext  openstudio_version

# May need this for syscalls that do not have ext in path
RUN ln -s /usr/local/openstudio-${OPENSTUDIO_VERSION}${OPENSTUDIO_VERSION_EXT} /usr/local/openstudio-${OPENSTUDIO_VERSION}

CMD [ "/bin/bash" ]

ARG OPENSTUDIO_VERSION=3.2.1
ARG OPENSTUDIO_VERSION_EXT=""
ARG OPENSTUDIO_DOWNLOAD_URL=https://openstudio-builds.s3.amazonaws.com/3.2.1/OpenStudio-3.2.1%2Bbdbdbc9da6-Ubuntu-18.04.deb

ENV OS_BUNDLER_VERSION=2.1.4
ENV RUBY_VERSION=2.7.2
ENV BUNDLE_WITHOUT=native_ext
# Install gdebi, then download and install OpenStudio, then clean up.
# gdebi handles the installation of OpenStudio's dependencies

# install locales and set to en_US.UTF-8. This is needed for running the CLI on some machines
# such as singularity.
RUN apt-get update && apt-get install -y \
        curl \
        vim \
        gdebi-core \
        libsqlite3-dev \
        libssl-dev \
        libffi-dev \
        build-essential \
        zlib1g-dev \
        vim \
        git \
        locales \
        sudo \
    && echo "OpenStudio Package Download URL is ${OPENSTUDIO_DOWNLOAD_URL}" \
    && curl -SLO $OPENSTUDIO_DOWNLOAD_URL \
    && OPENSTUDIO_DOWNLOAD_FILENAME=$(ls *.deb) \
    # Verify that the download was successful (not access denied XML from s3)
    && grep -v -q "<Code>AccessDenied</Code>" ${OPENSTUDIO_DOWNLOAD_FILENAME} \
    && gdebi -n $OPENSTUDIO_DOWNLOAD_FILENAME
    # Cleanup
    RUN rm -f $OPENSTUDIO_DOWNLOAD_FILENAME \
    && rm -rf /var/lib/apt/lists/* \
    && locale-gen en_US en_US.UTF-8 \
    && dpkg-reconfigure locales


RUN curl -SLO https://cache.ruby-lang.org/pub/ruby/2.7/ruby-2.7.2.tar.gz \
    && tar -xvzf ruby-2.7.2.tar.gz \
    && cd ruby-2.7.2 \
    && ./configure \
    && make && make install


## Add RUBYLIB link for openstudio.rb
ENV RUBYLIB=/usr/local/openstudio-${OPENSTUDIO_VERSION}${OPENSTUDIO_VERSION_EXT}/Ruby
ENV ENERGYPLUS_EXE_PATH=/usr/local/openstudio-${OPENSTUDIO_VERSION}${OPENSTUDIO_VERSION_EXT}/EnergyPlus/energyplus

# The OpenStudio Gemfile contains a fixed bundler version, so you have to install and run specific to that version
RUN gem install bundler -v $OS_BUNDLER_VERSION && \
  #AA commenting out since already done  mkdir /var/oscli && \
    ls /usr/local && \
    cp /usr/local/openstudio-${OPENSTUDIO_VERSION}${OPENSTUDIO_VERSION_EXT}/Ruby/Gemfile /var/oscli/ && \
    cp /usr/local/openstudio-${OPENSTUDIO_VERSION}${OPENSTUDIO_VERSION_EXT}/Ruby/Gemfile.lock /var/oscli/ && \
    cp /usr/local/openstudio-${OPENSTUDIO_VERSION}${OPENSTUDIO_VERSION_EXT}/Ruby/openstudio-gems.gemspec /var/oscli/
WORKDIR /var/oscli
RUN bundle -v
RUN bundle _${OS_BUNDLER_VERSION}_ install --path=gems --without=native_ext --jobs=4 --retry=3

# Configure the bootdir & confirm that openstudio is able to load the bundled gem set in /var/gemdata
VOLUME /var/simdata/openstudio
WORKDIR /var/simdata/openstudio
RUN openstudio --verbose --bundle /var/oscli/Gemfile --bundle_path /var/oscli/gems --bundle_without native_ext  openstudio_version

# May need this for syscalls that do not have ext in path
# RUN ln -s /usr/local/openstudio-${OPENSTUDIO_VERSION}${OPENSTUDIO_VERSION_EXT} /usr/local/openstudio-${OPENSTUDIO_VERSION} AA commenting out since already done

CMD [ "/bin/bash" ]

# Install required libaries.
#   realpath - needed for wait-for-it
RUN apt-get update && apt-get install -y wget gnupg \
    && wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | apt-key add - \
#RUN sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6 && \
    && echo "deb http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/4.4 multiverse" | \
    tee /etc/apt/sources.list.d/mongodb-org-4.4.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        apt-transport-https \
        autoconf \
        bison \
        shared-mime-info \
        build-essential \
        bzip2 \
        ca-certificates \
        curl \
        default-jdk \
        dos2unix \
        imagemagick \
        gdebi-core \
        git \
        libbz2-dev \
        libcurl4-openssl-dev \
        libdbus-glib-1-2 \
        libgdbm5 \
        libgdbm-dev \
        libglib2.0-dev \
        libglu1 \
        libgsl0-dev \
        libncurses-dev \
        libreadline-dev \
        libxml2-dev \
        libxslt-dev \
        libffi-dev \
        libssl-dev \
        libyaml-dev \
        libice-dev \
        libsm-dev \
        mongodb-database-tools \
        nodejs \
        procps \
        python-numpy \
        python3-numpy \
        python3.7-dev\
        tar \
        unzip \
        wget \
        zip \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install passenger (this also installs nginx)
ENV PASSENGER_VERSION 6.0.2

RUN gem install passenger -v $PASSENGER_VERSION
RUN passenger-install-nginx-module

# Configure the nginx server
RUN mkdir /var/log/nginx
ADD /docker/server/nginx.conf /opt/nginx/conf/nginx.conf

# Radiance env vars. RUBYLIB is set in the base openstudio container
ENV OPENSTUDIO_SERVER 'true'
ENV OS_RAYPATH /usr/local/openstudio-$OPENSTUDIO_VERSION/Radiance
ENV PERL_EXE_PATH /usr/bin

# Specify a couple arguments here, after running the majority of the installation above
ARG rails_env=docker
ARG bundle_args="--without development test"
ENV OS_BUNDLER_VERSION=2.1.4

# Set the rails env var
ENV RAILS_ENV $rails_env

# extension gem testing
#ENV FAVOR_LOCAL_GEMS 1

#### OpenStudio Server Code
# First upload the Gemfile* so that it can cache the Gems -- do this first because it is slow
ADD /bin /opt/openstudio/bin
ADD /server/Gemfile /opt/openstudio/server/Gemfile
WORKDIR /opt/openstudio/server
RUN bundle _${OS_BUNDLER_VERSION}_ install --jobs=3 --retry=3 $bundle_args

# Add the app assets and precompile assets. Do it this way so that when the app changes the assets don't
# have to be recompiled everytime
ADD /server/Rakefile /opt/openstudio/server/Rakefile
ADD /server/config/ /opt/openstudio/server/config/
ADD /server/app/assets/ /opt/openstudio/server/app/assets/

# Now call precompile
RUN mkdir /opt/openstudio/server/log
RUN bundle exec rake assets:precompile

# Bundle app source
ADD /server /opt/openstudio/server
# Add in /spec for testing
#ADD /spec /opt/openstudio/spec
ADD .rubocop.yml /opt/openstudio/.rubocop.yml
# Run bundle again, because if the user has a local Gemfile.lock it will have been overriden
RUN rm Gemfile.lock
RUN bundle install --jobs=3 --retry=3

# Add in scripts for running server. This includes the wait-for-it scripts to ensure other processes (mongo, redis) have
# started before starting the main process.
COPY /docker/server/wait-for-it.sh /usr/local/bin/wait-for-it
COPY /docker/server/start-server.sh /usr/local/bin/start-server

COPY /docker/server/rails-entrypoint.sh /usr/local/bin/rails-entrypoint
COPY /docker/server/start-web-background.sh /usr/local/bin/start-web-background
COPY /docker/server/start-workers.sh /usr/local/bin/start-workers
RUN chmod 755 /usr/local/bin/wait-for-it
RUN chmod +x /usr/local/bin/start-server
RUN chmod 755 /usr/local/bin/rails-entrypoint
RUN chmod 755 /usr/local/bin/start-web-background
RUN chmod 755 /usr/local/bin/start-workers

# set the permissions for windows users
RUN chmod +x /opt/openstudio/server/bin/*

ENTRYPOINT ["rails-entrypoint"]

CMD ["/usr/local/bin/start-server"]

# Expose ports.
EXPOSE 8080 9090
