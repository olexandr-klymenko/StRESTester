# StRESTester

## About

StRESTester is a Python tool for testing RESTful APIs compilant with [Swagger 1.2](https://github.com/swagger-api/swagger-spec/blob/master/versions/1.2.md) or [Swagger 2.0](https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md) specification.

## Example Usage

* create your <b><i>config.json</i></b> (there is <i>sample_config.json</i>)
* create your <b><i>scenario.xml</i></b> (there is <i>sample_scenario.xml</i>)
* <b>python3 -m pip install requirements.txt</b>
* <b>invoke run -c <i>config.json</i> -s <i>scenario.xml</i></b>

## Documentation

* <b><i>sample_config.json</i></b>
Will be published soon

* <b><i>sample_scenario.xml</i></b>
The scenario is XML file which contains sequence of so called <i>actions</i>.
Here are some action samples:

## Roadmap
* Implementing web socket logging handler for future web ui
* Implement web ui for stress test scenario generation and running and better report  output


## Contributing

1. Fork it ( http://github.com/olexandr-klymenko/StRESTester/fork )
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request
