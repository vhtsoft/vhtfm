<div align="center" markdown="1">
	<img src=".github/framework-logo-new.svg" width="80" height="80"/>
	<h1>Vhtfm Framework</h1>

 **Low Code Web Framework For Real World Applications, In Python And JavaScript**
</div>

<div align="center">
	<a target="_blank" href="#LICENSE" title="License: MIT"><img src="https://img.shields.io/badge/License-MIT-success.svg"></a>
	<a href="https://codecov.io/gh/vhtfm/vhtfm"><img src="https://codecov.io/gh/vhtfm/vhtfm/branch/develop/graph/badge.svg?token=XoTa679hIj"/></a>
</div>
<div align="center">
	<img src=".github/hero-image.png" alt="Hero Image" />
</div>
<div align="center">
    <a href="https://vhtfm.io/framework">Website</a>
    -
    <a href="https://docs.vhtfm.io/framework">Documentation</a>
</div>

## Vhtfm Framework
Full-stack web application framework that uses Python and MariaDB on the server side and a tightly integrated client side library. Built for ERPNext.

### Motivation
Started in 2005, Vhtfm Framework was inspired by the Semantic Web. The "big idea" behind semantic web was of a framework that not only described how information is shown (like headings, body etc), but also what it means, like name, address etc.

By creating a web framework that allowed for easy definition of metadata, it made building complex applications easy. Applications usually designed around how users interact with a system, but not based on semantics of the underlying system. Applications built on semantics end up being much more consistent and extensible. The first application built on Framework was ERPNext, a beast with more than 700 object types. Framework is not for the light hearted - it is not the first thing you might want to learn if you are beginning to learn web programming, but if you are ready to do real work, then Framework is the right tool for the job.

### Key Features

- **Full-Stack Framework**: Vhtfm covers both front-end and back-end development, allowing developers to build complete applications using a single framework.

- **Built-in Admin Interface**: Provides a pre-built, customizable admin dashboard for managing application data, reducing development time and effort.

- **Role-Based Permissions**: Comprehensive user and role management system to control access and permissions within the application.

- **REST API**: Automatically generated RESTful API for all models, enabling easy integration with other systems and services.

- **Customizable Forms and Views**: Flexible form and view customization using server-side scripting and client-side JavaScript.

- **Report Builder**: Powerful reporting tool that allows users to create custom reports without writing any code.

<details>
<summary>Screenshots</summary>

![List View](.github/fw-list-view.png)
![Form View](.github/fw-form-view.png)
![Role Permission Manager](.github/fw-rpm.png)
</details>

## Production Setup

### Managed Hosting

You can try [Vhtfm Cloud](https://vhtfmcloud.com), a simple, user-friendly and sophisticated [open-source](https://github.com/vhtfm/press) platform to host Vhtfm applications with peace of mind.

It takes care of installation, setup, upgrades, monitoring, maintenance and support of your Vhtfm deployments. It is a fully featured developer platform with an ability to manage and control multiple Vhtfm deployments.

<div>
    <a href="https://vhtfmcloud.com/" target="_blank">
        <picture>
            <source media="(prefers-color-scheme: dark)" srcset="https://vhtfm.io/files/try-on-fc-white.png">
            <img src="https://vhtfm.io/files/try-on-fc-black.png" alt="Try on Vhtfm Cloud" height="28" />
        </picture>
    </a>
</div>

### Self Hosting

### Docker
Prerequisites: docker, docker-compose, git. Refer [Docker Documentation](https://docs.docker.com) for more details on Docker setup.

Run following commands:

```
git clone https://github.com/vhtfm/vhtfm_docker
cd vhtfm_docker
docker compose -f pwd.yml up -d
```

After a couple of minutes, site should be accessible on your localhost port: 8080. Use below default login credentials to access the site.
- Username: Administrator
- Password: admin

See [Vhtfm Docker](https://github.com/vhtfm/vhtfm_docker?tab=readme-ov-file#to-run-on-arm64-architecture-follow-this-instructions) for ARM based docker setup.

## Development Setup
### Manual Install

The Easy Way: our install script for fox will install all dependencies (e.g. MariaDB). See https://github.com/vhtfm/fox for more details.

New passwords will be created for the Vhtfm "Administrator" user, the MariaDB root user, and the vhtfm user (the script displays the passwords and saves them to ~/vhtfm_passwords.txt).

### Local

To setup the repository locally follow the steps mentioned below:

1. Setup fox by following the [Installation Steps](https://docs.vhtfm.io/framework/user/en/installation) and start the server
   ```
   fox start
   ```

2. In a separate terminal window, run the following commands:
   ```
   # Create a new site
   fox new-site vhtfm.dev
   
   # Map your site to localhost
   fox --site vhtfm.dev add-to-hosts
   ```

3. Open the URL `http://vhtfm.dev:8000/app` in your browser, you should see the app running

## Learning and community

1. [Vhtfm School](https://vhtfm.school) - Learn Vhtfm Framework and ERPNext from the various courses by the maintainers or from the community.
2. [Official documentation](https://docs.vhtfm.io/framework) - Extensive documentation for Vhtfm Framework.
3. [Discussion Forum](https://discuss.vhtfm.io/) - Engage with community of Vhtfm Framework users and service providers.
4. [buildwithhussain.dev](https://buildwithhussain.dev) - Watch Vhtfm Framework being used in the wild to build world-class web apps.

## Contributing

1. [Issue Guidelines](https://github.com/vhtfm/vhterp/wiki/Issue-Guidelines)
1. [Report Security Vulnerabilities](https://vhtfm.io/security)
1. [Pull Request Requirements](https://github.com/vhtfm/vhterp/wiki/Contribution-Guidelines)

<br>
<br>
<div align="center">
	<a href="https://vhtfm.io" target="_blank">
		<picture>
			<source media="(prefers-color-scheme: dark)" srcset="https://vhtfm.io/files/Vhtfm-white.png">
			<img src="https://vhtfm.io/files/Vhtfm-black.png" alt="Vhtfm Technologies" height="28"/>
		</picture>
	</a>
</div>