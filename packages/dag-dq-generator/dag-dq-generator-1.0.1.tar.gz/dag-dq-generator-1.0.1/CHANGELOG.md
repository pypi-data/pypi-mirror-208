# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2023-05-13

### Major changes
- Updated `black` from `22.6.0` to `23.3.0`
- Updated `apache-airflow-providers-databricks` from `3.1.0` to `4.1.0`

### Changed features

- Feature: Added support for `SubGroupOperator` which enables the creation of subgroups in the DAG, theoritically allowing for infinite nesting of DAGs. Please visit the [documentation](https://wiki.corp.adobe.com/pages/viewpage.action?pageId=2849653154#Implementation&Use-SubGroupOperator) for more information
- Fix: N/A

## [1.0.0] - 2023-05-02

We're super excited to announce the release of v1.0 of the `dag-generator`!

This major release fully focuses on the production release of the generator.