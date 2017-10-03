# StRESTester

## About

StRESTester is a Python tool for testing RESTful APIs compilant with [Swagger 1.2](https://github.com/swagger-api/swagger-spec/blob/master/versions/1.2.md) or [Swagger 2.0](https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md) specification.

## Dependencies
* validators
* aiohttp
* invoke
* jinja2


## Example Usage

* create your <b><i>config.json</i></b> (there is <i>sample_config.json</i>)
* create your <b><i>scenario.xml</i></b> (there is <i>sample_scenario.xml</i>)
* <b>python3 -m pip install requirements.txt</b>
* <b>invoke run -c <i>config.json</i> -s <i>scenario.xml</i></b>

## Documentation

<b><i>sample_config.json</i></b>
<pre><code>
{
  "urls": {
    "api_url_1":  "http://127.0.0.1:8000",
    "api_url_2": "http://127.0.0.1:8080"
  },
  "users_number": 10,
  "iterations_number": 3,
  "workers_number": 6
}
</code></pre>
* _urls_ - list of api urls
* _users_number_ - number of test users making requests asyncroniously
* _workers_number_ - number of parallel processes of testing
* _iterations_number_ - number of stress test scenario iterations

<b><i>sample_scenario.xml</i></b>
``` xml
<scenario>
    <rest name="Create User">
        <method>POST</method>
        <url>{{ api_url_1 }}/accounts/</url>
        <data>{"login": "{{ username }}", "password": "{{ password }}"}</data>
    </rest>
    <rest name="Get Auth Token" return="token_1">
        <method>POST</method>
        <url>{{ api_url_1 }}/tokens/</url>
        <data>{"login": "{{ username }}", "password": "{{ password }}"}</data>
    </rest>
    <rest name="Login" return="token_2_info">
        <method>POST</method>
        <url>{{ api_url_2 }}/accounts/login/</url>
        <data>{{ token_1 }}</data>
        <raw>True</raw>
        <headers>{"content-type": "application/json"}</headers>
    </rest>
    <get name="get token_2" return="token_2">
        <info>{{ token_2_info }}</info>
        <key>token</key>
    </get>
    <rest name="Create Profile" return="user_info">
        <method>POST</method>
        <url>{{ api_url_2 }}/accounts/profile/</url>
        <data>{"nickname": "{{ username }}"}</data>
        <headers>{"content-type": "application/json", "Token": "{{ token_2 }}"}</headers>
        <raw>True</raw>
    </rest>
    <get name="get profile_info" return="profile_info">
        <info>{{ user_info }}</info>
        <key>profile</key>
    </get>
    <get name="get profile_id" return="profile_id">
        <info>{{ profile_info }}</info>
        <key>profile_id</key>
    </get>
    <get name="get user_id" return="user_id">
        <info>{{ profile_info }}</info>
        <key>user_id</key>
    </get>
    <repeat cycles="5">
        <rest name="Set user wallet to 10">
            <method>PUT</method>
            <url>{{ api }}/super/bank/{{ user_id }}</url>
            <data>{"amount": 10}</data>
            <headers>{"content-type": "application/json"}</headers>
            <raw>True</raw>
        </rest>
        <rest name="Get user wallet">
            <method>GET</method>
            <url>{{ api_url_2 }}/accounts/bank/</url>
            <headers>{"content-type": "application/json", "Token": "{{ token_2 }}" }</headers>
        </rest>
        <rest name="Patch money amount">
            <method>PATCH</method>
            <url>{{ api_url_2 }}/super/bank/{{ user_id }}</url>
            <data>{"amount": 10}</data>
            <headers>{"content-type": "application/json"}</headers>
            <raw>True</raw>
        </rest>
    </repeat>
    <rest name="Delete profile">
        <method>DELETE</method>
        <url>{{ api_url_2 }}/super/profiles/</url>
        <params>{"profile_id": "{{ profile_id }}", "user_id": "{{ user_id }}"}</params>
    </rest>
    <rest name="Delete User">
        <method>DELETE</method>
        <url>{{ api_url_1 }}/accounts/{{ username }}</url>
    </rest>
</scenario>
```
* scenario consists of snippets, so called actions (_'rest'_, _'get'_)
* list of actions can be extended
* each action must have mandatory attribute <b>_'name'_</b>
* attribute <b>_'return'_</b> intended for assignment return of action to given variable
* node <b>_'repeat'_</b> allows to create loops of scenario snippets, meaning of the attribute <b>_'cycles'_</b> is obvious
* jinja2 template is used to define action arguments

# Report output
* report output looks like
<pre><code>
Action metrics (averages):
{   'Create Profile': 0.162066854249167,
    'Create User': 0.29612173768576905,
    'Delete User': 0.07070714197972627,
    'Delete profile': 0.08907260841132114,
    'Get Auth Token': 0.2546299340232598,
    'Get user wallet': 0.012372952839989002,
    'Login': 0.03050658500530956,
    'Patch money amount': 0.09161834647939628,
    'Set user wallet to 10': 0.11090895620377335}
Error metrics:
{}
</code></pre>
values are excecution time of <b>rest</b> actions in seconds

## Roadmap
* Implement web ui for stress test scenario generation and running and better report  output
* Dockerize application


## Contributing

1. Fork it ( http://github.com/olexandr-klymenko/StRESTester/fork )
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request
