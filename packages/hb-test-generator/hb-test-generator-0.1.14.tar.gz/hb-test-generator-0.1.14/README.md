It writes tests and saves it into a file.

## Quality

As it's an AI, it's not perfect. It's a good start, but you should always review the generated tests.

## Requirements

- Python 3.6+
- OpenAI API key (You can obtain one from [platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys))

## Installation

1. Run: `pip install hb_test_generator`

2. Set the `OPENAI_API_KEY` environment variable with your OpenAI API key

## Usage examples

- `hb-generate-tests app/helpers/membership_helper.rb` will create a `spec/helpers/membership_helper_spec.rb`.
- `hb-generate-tests src/components/MyComponent.vue` will create a `tests/components/MyComponent.spec.js`. 

### Command alternatives
- `hb-generate-tests ...`
- `hb-generate-test ...`
- `hb-gen-tests ...`
- `hb-gen-test ...`

### Prompt
Create a `test_generator_prompt.txt` file containing the base prompt. Default prompt is:

```text
Write tests for below code. Name and place it according to best practices.
```

#### Example  for ruby on rails + rspec + factory_bot:
```text
Write rspec tests for below code. Use factory instead of yml fixtures if needed. Put it into `spec/` dir. Name format `*_spec.rb`.
```

#### Example for vue3 + jest:
```text
Write jest tests for below code. Put it into `tests/` dir near `src/` dir. Name format `*.spec.js`.
```


## Dev commands

`python3 setup.py sdist bdist_wheel`

`twine upload dist/*`
