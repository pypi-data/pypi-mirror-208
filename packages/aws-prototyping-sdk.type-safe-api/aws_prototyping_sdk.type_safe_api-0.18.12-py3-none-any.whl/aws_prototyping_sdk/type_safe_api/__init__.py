'''
## Type Safe API

Define your APIs using [Smithy](https://smithy.io/2.0/) or [OpenAPI v3](https://swagger.io/specification/), and leverage the power of generated client and server types, infrastructure, documentation, and automatic input validation!

This package vends a projen project type which allows you to define an API using either [Smithy](https://smithy.io/2.0/) or [OpenAPI v3](https://swagger.io/specification/), and a construct which manages deploying this API in API Gateway, given an integration (eg a lambda) for every operation.

The project will generate "runtime" projects from your API definition in your desired languages, which can be utilised both client side for interacting with your API, or server side for implementing your API. The project also generates a type-safe CDK construct which ensures an integration is provided for every API operation.

Code is generated at build time, so when you change your API model, just rebuild and you'll see your changes reflected in the generated code.

### Quick Start: TypeScript

This section describes how to get started quickly, with TypeScript infrastructure and lambda handlers. See the end of the README for examples in [Python](#quick-start--python) and [Java](#quick-start--python).

#### Create Your API Project

Use the project in your `.projenrc.ts`. It can either be part of an [`nx-monorepo`](../nx-monorepo/README.md) (recommended) or used in a standalone fashion.

```python
import { NxMonorepoProject } from "@aws-prototyping-sdk/nx-monorepo";
import { TypeSafeApiProject } from "@aws-prototyping-sdk/type-safe-api";
import { AwsCdkTypeScriptApp } from "projen/lib/awscdk";

// Create the monorepo
const monorepo = new NxMonorepoProject({ ... });

// Create the API project
const api = new TypeSafeApiProject({
  name: "myapi",
  parent: monorepo,
  outdir: 'packages/api',
  // Smithy as the model language. You can also use ModelLanguage.OPENAPI
  model: {
    language: ModelLanguage.SMITHY,
    options: {
      smithy: {
        serviceName: {
          namespace: 'com.mycompany',
          serviceName: 'MyApi',
        },
      },
    },
  },
  // Generate types, client and server code in TypeScript, Python and Java
  runtime: {
    languages: [Language.TYPESCRIPT, Language.PYTHON, Language.JAVA],
  },
  // CDK infrastructure in TypeScript
  infrastructure: {
    language: Language.TYPESCRIPT,
  },
  // Generate HTML documentation
  documentation: {
    formats: [DocumentationFormat.HTML_REDOC],
  },
  // Generate react-query hooks to interact with the UI from a React website
  library: {
    libraries: [Library.TYPESCRIPT_REACT_QUERY_HOOKS],
  },
});

// Create a CDK infrastructure project. Can also consider PDKPipelineTsProject as an alternative!
const infra = new AwsCdkTypeScriptApp({ ... });

// Infrastructure can depend on the generated API infrastructure and runtime
infra.addDeps(api.infrastructure.typescript!.package.packageName);
infra.addDeps(api.runtime.typescript!.package.packageName);

monorepo.synth();
```

#### Use the CDK Construct

In your CDK application (ie within the `infra` project we created), consume the `Api` construct, vended from the generated typescript infrastructure package.

```python
import { Stack, StackProps } from "aws-cdk-lib";
import { Construct } from "constructs";
import { Api } from "myapi-typescript-infra"; // <- generated typescript infrastructure package
import { Authorizers, Integrations } from "@aws-prototyping-sdk/type-safe-api";
import { NodejsFunction } from "aws-cdk-lib/aws-lambda-nodejs";
import { Cors } from "aws-cdk-lib/aws-apigateway";
import * as path from "path";

export class MyStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps = {}) {
    super(scope, id, props);

    // Instantiate the generated CDK construct to deploy an API Gateway API based on your model
    new Api(this, "MyApi", {
      defaultAuthorizer: Authorizers.iam(),
      corsOptions: {
        allowOrigins: Cors.ALL_ORIGINS,
        allowMethods: Cors.ALL_METHODS,
      },
      // Supply an integration for every operation
      integrations: {
        sayHello: {
          integration: Integrations.lambda(
            new NodejsFunction(this, "SayHelloLambda", {
              entry: path.resolve(__dirname, "say-hello.ts"),
            })
          ),
        },
      },
    });
  }
}
```

#### Implement a Lambda Handler

The generated runtime projects include lambda handler wrappers which provide type-safety for implementing your API operations. You can implement your lambda handlers in any of the supported languages, and even mix and match languages for different operations if you like.

In the above CDK application, we used `NodejsFunction` with the entry point as `say-hello.ts`, so we can define the lambda function in the same `infra` project.

In typescript, the implementation of `say-hello.ts` would look like:

```python
import { sayHelloHandler } from "myapi-typescript-runtime"; // <- generated typescript runtime package

// Use the handler wrapper for type-safety to ensure you correctly implement your modelled API operation
export const handler = sayHelloHandler(async ({ input }) => {
  return {
    statusCode: 200,
    body: {
      message: `Hello ${input.requestParameters.name}`,
    },
  };
});
```

### Project

The `TypeSafeApiProject` projen project sets up the project structure for you. You have a few parameters to consider when creating the project:

* `model` - Configure the API model. Select a `language` for the model of either [Smithy](https://smithy.io/2.0/) or [OpenAPI v3](https://swagger.io/specification/), and supply `options.smithy` or `options.openapi` depending on your choice.
* `runtime` - Configure the generated runtime projects. Include one or more `languages` you wish to write your client and server-side code in. These projects contain generated types defined in your model, as well as type-safe lambda handler wrappers for implementing each operation.
* `infrastructure` - Pick the `language` you are writing your CDK infrastructure in. A construct will be generated in this language which can be used to deploy the API.
* `documentation` - Specify `formats` to generate documentation in.

It's recommended that these projects are used as part of an `nx-monorepo` project (eg. by specifying `parent: myMonorepoProject`), as it makes setting up dependencies much easier, particularly when extending your project further with a CDK app and lambda functions.

Depending on the `model.language` you choose, you must supply the corresponding `model.options`. For example:

```python
new TypeSafeApiProject({
  model: {
    language: ModelLanguage.SMITHY,
    options: {
      smithy: {
        serviceName: {
          namespace: 'com.mycompany',
          serviceName: 'MyApi',
        },
      },
    },
  },
  ...
});
```

```python
new TypeSafeApiProject({
  model: {
    language: ModelLanguage.OPENAPI,
    options: {
      openapi: {
        title: 'MyApi',
      },
    },
  },
  ...
});
```

`model.options.smithy` allows for further customisation of the Smithy project, eg:

```python
new TypeSafeApiProject({
  model: {
    language: ModelLanguage.SMITHY,
    options: {
      smithy: {
        serviceName: {
          namespace: 'com.mycompany',
          serviceName: 'MyApi',
        },
        // By default, the contents of the smithy build output directory `model/output` will be ignored by source control.
        // Set this to false to include it, for example if you are generating clients directly from the smithy model.
        ignoreSmithyBuildOutput: false,
        // The gradle wrapper used for the smithy build is copied from the PDK itself if it does not already exist in
        // the 'smithy' folder. By default, this gradle wrapper will be ignored by source control.
        // Set this to false if you would like to check the gradle wrapper in to source control, for example if you want
        // to use a different version of the gradle wrapper in your project.
        ignoreGradleWrapper: false,
        // Use smithyBuildOptions to control what is added to smithy-build.json.
        smithyBuildOptions: {
          projections: {
            // You can customise the built-in openapi projection, used to generate the OpenAPI specification.
            openapi: {
              plugins: {
                openapi: {
                  // Customise the openapi projection here.
                  // See: https://smithy.io/2.0/guides/converting-to-openapi.html
                  useIntegerType: true,
                  ...
                }
              }
            },
            // You can add new projections here too
            "ts-client": {
              "plugins": {
                "typescript-codegen": {
                  "package" : "@my-test/smithy-generated-typescript-client",
                  "packageVersion": "0.0.1"
                }
              }
            }
          },
          // Note that any additional dependencies required for projections/plugins can be added here, which in turn will
          // add them to the `smithy/build.gradle` file
          maven: {
            dependencies: [
              "software.amazon.smithy:smithy-validation-model:1.27.2",
            ]
          }
        }
      },
    }
  },
  ...
});
```

#### Directory Structure

The `TypeSafeApiProject` will create the following directory structure within its `outdir`:

```
|_ model/
    |_ src/
        |_ main/
            |_ smithy - your API definition if you chose ModelLanguage.SMITHY
            |_ openapi - your API definition if you chose ModelLanguage.OPENAPI
|_ runtime/ - generated types, client, and server code in the languages you specified
    |_ typescript
    |_ python
    |_ java
|_ infrastructure/ - generated infrastructure (you'll find only one directory in here based on your chosen infrastructure language)
    |_ typescript
    |_ python
    |_ java
|_ documentation/ - generated documentation in the formats you specified
    |_ html2
    |_ html_redoc
    |_ plantuml
    |_ markdown
|_ library/ - generated libraries if specified
    |_ typescript-react-query-hooks
```

### Smithy IDL

Please refer to the [Smithy documentation](https://smithy.io/2.0/quickstart.html) for how to write models in Smithy. A basic example is provided below:

```smithy
$version: "2"
namespace example.hello

use aws.protocols#restJson1

@title("A Sample Hello World API")

/// A sample smithy api
@restJson1
service Hello {
    version: "1.0"
    operations: [SayHello]
}

@readonly
@http(method: "GET", uri: "/hello")
operation SayHello {
    input: SayHelloInput
    output: SayHelloOutput
    errors: [ApiError]
}

string Name
string Message

@input
structure SayHelloInput {
    @httpQuery("name")
    @required
    name: Name
}

@output
structure SayHelloOutput {
    @required
    message: Message
}

@error("client")
structure ApiError {
    @required
    errorMessage: Message
}
```

#### Supported Protocols

Currently only [AWS restJson1](https://smithy.io/2.0/aws/protocols/aws-restjson1-protocol.html) is supported. Please ensure your service is annotated with the `@restJson1` trait.

#### Multiple Files

You can split your definition into multiple files and folders, so long as they are all under the `model/src/main/smithy` directory in your API project.

#### Authorizers

Smithy supports [adding API Gateway authorizers in the model itself](https://smithy.io/2.0/aws/aws-auth.html). Given that at model definition time one usually does not know the ARN of the user pool or lambda function for an authorizer, it is recommended to add the authorizer(s) in your Api CDK construct.

If using Smithy generated clients, some authorizer traits (eg sigv4) will include configuring the client for that particular method of authorization, so it can be beneficial to still define authorizers in the model. We therefore support specifying authorizers in both the model and the construct, but note that the construct will take precedence where the authorizer ID is the same.

### OpenAPI Specification

Your `model/src/main/openapi/main.yaml` file defines your api using [OpenAPI Version 3.0.3](https://swagger.io/specification/). An example spec might look like:

```yaml
openapi: 3.0.3
info:
  version: 1.0.0
  title: Example API
paths:
  /hello:
    get:
      operationId: sayHello
      parameters:
        - in: query
          name: name
          schema:
            type: string
          required: true
      responses:
        "200":
          description: Successful response
          content:
            "application/json":
              schema:
                $ref: "#/components/schemas/HelloResponse"
components:
  schemas:
    HelloResponse:
      type: object
      properties:
        message:
          type: string
      required:
        - message
```

You can divide your specification into multiple files using `$ref`.

For example, you might choose to structure your spec as follows:

```
|_ model/src/main/openapi/
    |_ main.yaml
    |_ paths/
        |_ index.yaml
        |_ sayHello.yaml
    |_ schemas/
        |_ index.yaml
        |_ helloResponse.yaml
```

Where `main.yaml` looks as follows:

```yaml
openapi: 3.0.3
info:
  version: 1.0.0
  title: Example API
paths:
  $ref: "./paths/index.yaml"
components:
  schemas:
    $ref: "./schemas/index.yaml"
```

`paths/index.yaml`:

```yaml
/hello:
  get:
    $ref: "./sayHello.yaml"
```

`paths/sayHello.yaml`:

```yaml
operationId: sayHello
parameters:
  - in: query
    name: name
    schema:
      type: string
    required: true
responses:
  "200":
    description: Successful response
    content:
      "application/json":
        schema:
          $ref: "../schemas/helloResponse.yaml"
```

`schemas/index.yaml`:

```yaml
HelloResponse:
  $ref: "./helloResponse.yaml"
```

`schemas/helloResponse.yaml`:

```yaml
type: object
properties:
  message:
    type: string
required:
  - message
```

### Construct

A CDK construct is generated in the `infrastructure/<language>` directory which provides a type-safe interface for creating an API Gateway API based on your model.

You can extend or instantiate this construct in your CDK infrastructure project. You'll get a type error if you forget to define an integration for an operation defined in your api.

```python
import { Authorizers, Integrations } from "@aws-prototyping-sdk/type-safe-api";
import { NodejsFunction } from "aws-cdk-lib/aws-lambda-nodejs";
import { Construct } from "constructs";
import { Api } from "myapi-typescript-infra";

/**
 * An example of how to wire lambda handler functions to the API
 */
export class SampleApi extends Api {
  constructor(scope: Construct, id: string) {
    super(scope, id, {
      defaultAuthorizer: Authorizers.iam(),
      integrations: {
        // Every operation defined in your API must have an integration defined!
        sayHello: {
          integration: Integrations.lambda(
            new NodejsFunction(scope, "say-hello")
          ),
        },
      },
    });
  }
}
```

#### Sharing Integrations

If you would like to use the same integration for every operation (for example you'd like to use a single lambda function to service all requests with the in-built [handler router](#handler-router)), you can use the `Operations.all` method from a generated runtime project to save repeating yourself:

```python
import { Operations } from "myapi-typescript-runtime";
import { Authorizers, Integrations } from "@aws-prototyping-sdk/type-safe-api";
import { NodejsFunction } from "aws-cdk-lib/aws-lambda-nodejs";
import { Construct } from "constructs";
import { Api } from "myapi-typescript-infra";

export class SampleApi extends Api {
  constructor(scope: Construct, id: string) {
    super(scope, id, {
      defaultAuthorizer: Authorizers.iam(),
      // Use the same integration for every operation.
      integrations: Operations.all({
        integration: Integrations.lambda(new NodejsFunction(scope, "router")),
      }),
    });
  }
}
```

TypeScript is demonstrated above, but this is also available in Java and Python.

#### Authorizers

The `Api` construct allows you to define one or more authorizers for securing your API. An integration will use the `defaultAuthorizer` unless an `authorizer` is specified at the integration level. The following authorizers are supported:

* `Authorizers.none` - No auth
* `Authorizers.iam` - AWS IAM (Signature Version 4)
* `Authorizers.cognito` - Cognito user pool
* `Authorizers.custom` - A custom authorizer

##### Cognito Authorizer

To use the Cognito authorizer, one or more user pools must be provided. You can optionally specify the scopes to check if using an access token. You can use the `withScopes` method to use the same authorizer but verify different scopes for individual integrations, for example:

```python
export class SampleApi extends Api {
  constructor(scope: Construct, id: string) {
    const cognitoAuthorizer = Authorizers.cognito({
      authorizerId: "myCognitoAuthorizer",
      userPools: [new UserPool(scope, "UserPool")],
    });

    super(scope, id, {
      defaultAuthorizer: cognitoAuthorizer,
      integrations: {
        // Everyone in the user pool can call this operation:
        sayHello: {
          integration: Integrations.lambda(
            new NodejsFunction(scope, "say-hello")
          ),
        },
        // Only users with the given scopes can call this operation
        myRestrictedOperation: {
          integration: Integrations.lambda(
            new NodejsFunction(scope, "my-restricted-operation")
          ),
          authorizer: cognitoAuthorizer.withScopes(
            "my-resource-server/my-scope"
          ),
        },
      },
    });
  }
}
```

For more information about scopes or identity and access tokens, please see the [API Gateway documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-integrate-with-cognito.html).

##### Custom Authorizer

Custom authorizers use lambda functions to handle authorizing requests. These can either be simple token-based authorizers, or more complex request-based authorizers. See the [API Gateway documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html) for more details.

An example token-based authorizer (default):

```python
Authorizers.custom({
  authorizerId: "myTokenAuthorizer",
  function: new NodejsFunction(scope, "authorizer"),
});
```

An example request-based handler. By default the identitySource will be `method.request.header.Authorization`, however you can customise this as per [the API Gateway documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html#cfn-apigateway-authorizer-identitysource).

```python
Authorizers.custom({
  authorizerId: "myRequestAuthorizer",
  type: CustomAuthorizerType.REQUEST,
  identitySource:
    "method.request.header.MyCustomHeader, method.request.querystring.myQueryString",
  function: new NodejsFunction(scope, "authorizer"),
});
```

#### Integrations

Integrations are used by API Gateway to service requests.

##### Lambda Integration

Currently, the only built-in integration is a lambda integration. You can construct one using `Integrations.lambda(yourLambdaFunction)`.

##### Custom Integrations

You can implement your own integrations by inheriting the `Integration` class and implementing its `render` method. This method is responsible for returning a snippet of OpenAPI which will be added as the `x-amazon-apigateway-integration` for an operation. Please refer to the [API Gateway Swagger Extensions documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-swagger-extensions-integration.html) for more details.

You can also optionally override the `grant` method if you need to use CDK to grant API Gateway access to invoke your integration.

### Runtime: Clients

The generated runtime projects include clients which can be used for type-safe interaction with your API.

#### Typescript

The [typescript-fetch](https://openapi-generator.tech/docs/generators/typescript-fetch/) OpenAPI generator is used to generate typescript client. This requires an implementation of `fetch` to be passed to the client. In the browser one can pass the built in fetch, or in NodeJS you can use an implementation such as [node-fetch](https://www.npmjs.com/package/node-fetch).

Example usage of the client in a website:

```python
import { Configuration, DefaultApi } from "myapi-typescript-runtime";

const client = new DefaultApi(
  new Configuration({
    basePath: "https://xxxxxxxxxx.execute-api.ap-southeast-2.amazonaws.com",
    fetchApi: window.fetch.bind(window),
  })
);

await client.sayHello({ name: "Jack" });
```

#### Python

The [python](https://openapi-generator.tech/docs/generators/python) OpenAPI generator is used to generate clients for python.

Example usage:

```python
from myapi_python_runtime import ApiClient, Configuration
from myapi_python_runtime.api.default_api import DefaultApi

configuration = Configuration(
    host = "https://xxxxxxxxxx.execute-api.ap-southeast-2.amazonaws.com"
)

with ApiClient(configuration) as api_client:
    client = DefaultApi(api_client)

    client.say_hello(
        query_params={
            'name': "name_example",
        },
    )
```

You'll find details about how to use the python client in the README.md in your generated runtime project.

#### Java

The [java](https://openapi-generator.tech/docs/generators/java/) OpenAPI generator is used to generate clients for Java.

Example usage:

```java
import com.generated.api.myapijavaruntime.runtime.api.DefaultApi;
import com.generated.api.myapijavaruntime.runtime.ApiClient;
import com.generated.api.myapijavaruntime.runtime.Configuration;
import com.generated.api.myapijavaruntime.runtime.models.HelloResponse;

ApiClient client = Configuration.getDefaultApiClient();
client.setBasePath("https://xxxxxxxxxx.execute-api.ap-southeast-2.amazonaws.com");

DefaultApi api = new DefaultApi(client);
HelloResponse response = api.sayHello("Adrian").execute()
```

You'll find more details about how to use the Java client in the README.md in your generated runtime project.

### Lambda Handler Wrappers

Lambda handler wrappers are also importable from the generated runtime projects. These provide input/output type safety, ensuring that your API handlers return outputs that correspond to your model.

#### Typescript

```python
import { sayHelloHandler } from "myapi-typescript-runtime";

export const handler = sayHelloHandler(async ({ input }) => {
  return {
    statusCode: 200,
    body: {
      message: `Hello ${input.requestParameters.name}!`,
    },
  };
});
```

##### Handler Router

The lambda handler wrappers can be used in isolation as handler methods for separate lambdas. If you would like to use a single lambda function to serve all requests, you can do so with the `handlerRouter`.

```python
import {
  handlerRouter,
  sayHelloHandler,
  sayGoodbyeHandler,
} from "myapi-typescript-runtime";
import { corsInterceptor } from "./interceptors";
import { sayGoodbye } from "./handlers/say-goodbye";

const sayHello = sayHelloHandler(async ({ input }) => {
  return {
    statusCode: 200,
    body: {
      message: `Hello ${input.requestParameters.name}!`,
    },
  };
});

export const handler = handlerRouter({
  // Interceptors declared in this list will apply to all operations
  interceptors: [corsInterceptor],
  // Assign handlers to each operation here
  handlers: {
    sayHello,
    sayGoodbye,
  },
});
```

#### Python

```python
from myapi_python_runtime.apis.tags.default_api_operation_config import say_hello_handler, SayHelloRequest, ApiResponse, SayHelloOperationResponses
from myapi_python_runtime.model.api_error import ApiError
from myapi_python_runtime.model.hello_response import HelloResponse

@say_hello_handler
def handler(input: SayHelloRequest, **kwargs) -> SayHelloOperationResponses:
    return ApiResponse(
        status_code=200,
        body=HelloResponse(message="Hello {}!".format(input.request_parameters["name"])),
        headers={}
    )
```

##### Handler Router

The lambda handler wrappers can be used in isolation as handler methods for separate lambdas. If you would like to use a single lambda function to serve all requests, you can do so with the `handler_router`.

```python
from myapi_python_runtime.apis.tags.default_api_operation_config import say_hello_handler, SayHelloRequest, ApiResponse, SayHelloOperationResponses, handler_router, HandlerRouterHandlers
from myapi_python_runtime.model.api_error import ApiError
from myapi_python_runtime.model.hello_response import HelloResponse
from other_handlers import say_goodbye
from my_interceptors import cors_interceptor

@say_hello_handler
def say_hello(input: SayHelloRequest, **kwargs) -> SayHelloOperationResponses:
    return ApiResponse(
        status_code=200,
        body=HelloResponse(message="Hello {}!".format(input.request_parameters["name"])),
        headers={}
    )

handler = handler_router(
  # Interceptors defined here will apply to all operations
  interceptors=[cors_interceptor],
  handlers=HandlerRouterHandlers(
    say_hello=say_hello,
    say_goodbye=say_goodbye
  )
)
```

#### Java

```java
import com.generated.api.myapijavaruntime.runtime.api.Handlers.SayHello;
import com.generated.api.myapijavaruntime.runtime.api.Handlers.SayHello200Response;
import com.generated.api.myapijavaruntime.runtime.api.Handlers.SayHelloRequestInput;
import com.generated.api.myapijavaruntime.runtime.api.Handlers.SayHelloResponse;
import com.generated.api.myapijavaruntime.runtime.model.HelloResponse;


public class SayHelloHandler extends SayHello {
    @Override
    public SayHelloResponse handle(SayHelloRequestInput sayHelloRequestInput) {
        return SayHello200Response.of(HelloResponse.builder()
                .message(String.format("Hello %s", sayHelloRequestInput.getInput().getRequestParameters().getName()))
                .build());
    }
}
```

##### Handler Router

The lambda handler wrappers can be used in isolation as handler methods for separate lambdas. If you would like to use a single lambda function to serve all requests, you can do so by extending the `HandlerRouter` class.

```java
import com.generated.api.myapijavaruntime.runtime.api.Handlers.SayGoodbye;
import com.generated.api.myapijavaruntime.runtime.api.Handlers.HandlerRouter;
import com.generated.api.myapijavaruntime.runtime.api.Handlers.Interceptors;
import com.generated.api.myapijavaruntime.runtime.api.Handlers.SayHello;

import java.util.Arrays;
import java.util.List;

// Interceptors defined here apply to all operations
@Interceptors({ TimingInterceptor.class })
public class ApiHandlerRouter extends HandlerRouter {
    // You must implement a method to return a handler for every operation
    @Override
    public SayHello sayHello() {
        return new SayHelloHandler();
    }

    @Override
    public SayGoodbye sayGoodbye() {
        return new SayGoodbyeHandler();
    }
}
```

### Interceptors

The lambda handler wrappers allow you to pass in a *chain* of handler functions to handle the request. This allows you to implement middleware / interceptors for handling requests. Each handler function may choose whether or not to continue the handler chain by invoking `chain.next`.

#### Typescript

In typescript, interceptors are passed as separate arguments to the generated handler wrapper, in the order in which they should be executed. Call `request.chain.next(request)` from an interceptor to delegate to the rest of the chain to handle a request. Note that the last handler in the chain (ie the actual request handler which transforms the input to the output) should not call `chain.next`.

```python
import {
  sayHelloHandler,
  ChainedRequestInput,
  OperationResponse,
} from "myapi-typescript-runtime";

// Interceptor to wrap invocations in a try/catch, returning a 500 error for any unhandled exceptions.
const tryCatchInterceptor = async <
  RequestParameters,
  RequestArrayParameters,
  RequestBody,
  Response
>(
  request: ChainedRequestInput<
    RequestParameters,
    RequestArrayParameters,
    RequestBody,
    Response
  >
): Promise<Response | OperationResponse<500, { errorMessage: string }>> => {
  try {
    return await request.chain.next(request);
  } catch (e: any) {
    return { statusCode: 500, body: { errorMessage: e.message } };
  }
};

// tryCatchInterceptor is passed first, so it runs first and calls the second argument function (the request handler) via chain.next
export const handler = sayHelloHandler(
  tryCatchInterceptor,
  async ({ input }) => {
    return {
      statusCode: 200,
      body: {
        message: `Hello ${input.requestParameters.name}!`,
      },
    };
  }
);
```

Another example interceptor might be to record request time metrics. The example below includes the full generic type signature for an interceptor:

```python
import { ChainedRequestInput } from "myapi-typescript-runtime";

const timingInterceptor = async <
  RequestParameters,
  RequestArrayParameters,
  RequestBody,
  Response
>(
  request: ChainedRequestInput<
    RequestParameters,
    RequestArrayParameters,
    RequestBody,
    Response
  >
): Promise<Response> => {
  const start = Date.now();
  const response = await request.chain.next(request);
  const end = Date.now();
  console.log(`Took ${end - start} ms`);
  return response;
};
```

Interceptors may mutate the `interceptorContext` to pass state to further interceptors or the final lambda handler, for example an `identityInterceptor` might want to extract the authenticated user from the request so that it is available in handlers.

```python
import {
  LambdaRequestParameters,
  LambdaHandlerChain,
} from "myapi-typescript-runtime";

const identityInterceptor = async <
  RequestParameters,
  RequestArrayParameters,
  RequestBody,
  Response
>(
  request: ChainedRequestInput<
    RequestParameters,
    RequestArrayParameters,
    RequestBody,
    Response
  >
): Promise<Response> => {
  const authenticatedUser = await getAuthenticatedUser(request.event);
  return await request.chain.next({
    ...request,
    interceptorContext: {
      ...request.interceptorContext,
      authenticatedUser,
    },
  });
};
```

#### Python

In Python, a list of interceptors can be passed as a keyword argument to the generated lambda handler decorator, for example:

```python
from myapi_python_runtime.apis.tags.default_api_operation_config import say_hello_handler, SayHelloRequest, ApiResponse, SayHelloOperationResponses
from myapi_python_runtime.model.api_error import ApiError
from myapi_python_runtime.model.hello_response import HelloResponse

@say_hello_handler(interceptors=[timing_interceptor, try_catch_interceptor])
def handler(input: SayHelloRequest, **kwargs) -> SayHelloOperationResponses:
    return ApiResponse(
        status_code=200,
        body=HelloResponse(message="Hello {}!".format(input.request_parameters["name"])),
        headers={}
    )
```

Writing an interceptor is just like writing a lambda handler. Call `chain.next(input)` from an interceptor to delegate to the rest of the chain to handle a request.

```python
import time
from myapi_python_runtime.apis.tags.default_api_operation_config import ChainedApiRequest, ApiResponse

def timing_interceptor(input: ChainedApiRequest) -> ApiResponse:
    start = int(round(time.time() * 1000))
    response = input.chain.next(input)
    end = int(round(time.time() * 1000))
    print("Took {} ms".format(end - start))
    return response
```

Interceptors may choose to return different responses, for example to return a 500 response for any unhandled exceptions:

```python
import time
from myapi_python_runtime.model.api_error import ApiError
from myapi_python_runtime.apis.tags.default_api_operation_config import ChainedApiRequest, ApiResponse

def try_catch_interceptor(input: ChainedApiRequest) -> ApiResponse:
    try:
        return input.chain.next(input)
    except Exception as e:
        return ApiResponse(
            status_code=500,
            body=ApiError(errorMessage=str(e)),
            headers={}
        )
```

Interceptors are permitted to mutate the "interceptor context", which is a `Dict[str, Any]`. Each interceptor in the chain, and the final handler, can access this context:

```python
def identity_interceptor(input: ChainedApiRequest) -> ApiResponse:
    input.interceptor_context["AuthenticatedUser"] = get_authenticated_user(input.event)
    return input.chain.next(input)
```

Interceptors can also mutate the response returned by the handler chain. An example use case might be adding cross-origin resource sharing headers:

```python
def add_cors_headers_interceptor(input: ChainedApiRequest) -> ApiResponse:
    response = input.chain.next(input)
    return ApiResponse(
        status_code=response.status_code,
        body=response.body,
        headers={
            **response.headers,
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )
```

#### Java

In Java, interceptors can be added to a handler via the `@Interceptors` class annotation:

```java
import com.generated.api.myjavaapiruntime.runtime.api.Handlers.Interceptors;

@Interceptors({ TimingInterceptor.class, TryCatchInterceptor.class })
public class SayHelloHandler extends SayHello {
    @Override
    public SayHelloResponse handle(SayHelloRequestInput sayHelloRequestInput) {
        return SayHello200Response.of(HelloResponse.builder()
                .message(String.format("Hello %s", sayHelloRequestInput.getInput().getRequestParameters().getName()))
                .build());
    }
}
```

To write an interceptor, you can implement the `Interceptor` interface. For example, a timing interceptor:

```java
import com.generated.api.myjavaapiruntime.runtime.api.Handlers.Interceptor;
import com.generated.api.myjavaapiruntime.runtime.api.Handlers.ChainedRequestInput;
import com.generated.api.myjavaapiruntime.runtime.api.Handlers.Response;

public class TimingInterceptor<Input> implements Interceptor<Input> {
    @Override
    public Response handle(ChainedRequestInput<Input> input) {
        long start = System.currentTimeMillis();
        Response res = input.getChain().next(input);
        long end = System.currentTimeMillis();
        System.out.printf("Took %d ms%n", end - start);
        return res;
    }
}
```

Interceptors may choose to return different responses, for example to return a 500 response for any unhandled exceptions:

```java
import com.generated.api.myjavaapiruntime.runtime.api.Handlers.Interceptor;
import com.generated.api.myjavaapiruntime.runtime.api.Handlers.ChainedRequestInput;
import com.generated.api.myjavaapiruntime.runtime.api.Handlers.Response;
import com.generated.api.myjavaapiruntime.runtime.api.Handlers.ApiResponse;
import com.generated.api.myjavaapiruntime.runtime.model.ApiError;

public class TryCatchInterceptor<Input> implements Interceptor<Input> {
    @Override
    public Response handle(ChainedRequestInput<Input> input) {
        try {
            return input.getChain().next(input);
        } catch (Exception e) {
            return ApiResponse.builder()
                    .statusCode(500)
                    .body(ApiError.builder()
                            .errorMessage(e.getMessage())
                            .build().toJson())
                    .build();
        }
    }
}
```

Interceptors are permitted to mutate the "interceptor context", which is a `Map<String, Object>`. Each interceptor in the chain, and the final handler, can access this context:

```java
public class IdentityInterceptor<Input> implements Interceptor<Input> {
    @Override
    public Response handle(ChainedRequestInput<Input> input) {
        input.getInterceptorContext().put("AuthenticatedUser", this.getAuthenticatedUser(input.getEvent()));
        return input.getChain().next(input);
    }
}
```

Interceptors can also mutate the response returned by the handler chain. An example use case might be adding cross-origin resource sharing headers:

```java
public static class AddCorsHeadersInterceptor<Input> implements Interceptor<Input> {
    @Override
    public Response handle(ChainedRequestInput<Input> input) {
        Response res = input.getChain().next(input);
        res.getHeaders().put("Access-Control-Allow-Origin", "*");
        res.getHeaders().put("Access-Control-Allow-Headers", "*");
        return res;
    }
}
```

##### Interceptors with Dependency Injection

Interceptors referenced by the `@Interceptors` annotation must be constructable with no arguments. If more complex instantiation of your interceptor is required (for example if you are using dependency injection or wish to pass configuration to your interceptor), you may instead override the `getInterceptors` method in your handler:

```java
public class SayHelloHandler extends SayHello {
    @Override
    public List<Interceptor<SayHelloInput>> getInterceptors() {
        return Arrays.asList(
                new MyConfiguredInterceptor<>(42),
                new MyOtherConfiguredInterceptor<>("configuration"));
    }

    @Override
    public SayHelloResponse handle(SayHelloRequestInput sayHelloRequestInput) {
        return SayHello200Response.of(HelloResponse.builder()
                .message(String.format("Hello %s!", sayHelloRequestInput.getInput().getRequestParameters().getName()))
                .build());
    }
}
```

### Libraries

Libraries are generated code projects which are not fully-fledged runtime languages.

#### TypeScript React Query Hooks

This library contains generated [react-query](https://tanstack.com/query/latest) hooks for interacting with your API from a React website. You can generate these by adding the following options to your `TypeSafeApiProject` in your `.projenrc`:

```python
new TypeSafeApiProject({
  library: {
    libraries: [Library.TYPESCRIPT_REACT_QUERY_HOOKS],
  },
  ...
});
```

##### Usage in a React Website

First, make sure you add a dependency on the generated hooks library, eg in your `.projenrc`:

```python
const api = new TypeSafeApiProject({ ... });

new CloudscapeReactTsWebsite({
  ...,
  deps: [
    ...
    api.library.typescriptReactQueryHooks!.package.packageName,
  ],
});
```

Next, create an instance of the API client (making sure to set the base URL and fetch instance). For example:

```python
// NB: client may be named differently if you have tagged your operations
import { DefaultApi } from "myapi-typescript-react-query-hooks";

export const useApiClient = () =>
  useMemo(
    () =>
      new DefaultApi(
        new Configuration({
          basePath:
            "https://example123.execute-api.ap-southeast-2.amazonaws.com/prod",
          fetchApi: window.fetch.bind(window),
        })
      ),
    []
  );
```

Note that if you are using the [Cloudscape React Website](../cloudscape-react-ts-website/README.md) with [AWS NorthStar](https://aws.github.io/aws-northstar/) and IAM (Sigv4) Auth for your API, you can use NorthStar's [`useSigv4Client()` hook](https://aws.github.io/aws-northstar/?path=/story/components-cognitoauth-sigv4client-docs--page) to create
an instance of `fetch` which will sign requests with the logged in user's credentials. For example:

```python
export const useApiClient = () => {
  const client = useSigv4Client();
  return useMemo(
    () =>
      new DefaultApi(
        new Configuration({
          basePath:
            "https://example123.execute-api.ap-southeast-2.amazonaws.com/prod",
          fetchApi: client,
        })
      ),
    [client]
  );
};
```

Next, instantiate the client provider above where you would like to use the hooks in your component hierarchy (such as above your router). For example:

```tsx
// NB: client provider may be named differently if you have tagged your operations
import { DefaultApiClientProvider } from "myapi-typescript-react-query-hooks";

const api = useApiClient();

return (
  <DefaultApiClientProvider apiClient={api}>
    {/* Components within the provider may make use of the hooks */}
  </DefaultApiClientProvider>
);
```

Finally, you can import and use your generated hooks. For example:

```tsx
import { useSayHello } from "myapi-typescript-react-query-hooks";

export const MyComponent: FC<MyComponentProps> = () => {
  const sayHello = useSayHello({ name: "World" });

  return sayHello.isLoading ? (
    <p>Loading...</p>
  ) : sayHello.isError ? (
    <p>Error!</p>
  ) : (
    <h1>{sayHello.data.message}</h1>
  );
};
```

##### Paginated Operations

You can generate `useInfiniteQuery` hooks instead of `useQuery` hooks for paginated API operations, by making use of the vendor extension `x-paginated` in your operation in the OpenAPI specification. You must specify both the `inputToken` and `outputToken`, which indicate the properties from the input and output used for pagination. For example in OpenAPI:

```yaml
paths:
  /pets:
    get:
      x-paginated:
        # Input property with the token to request the next page
        inputToken: nextToken
        # Output property with the token to request the next page
        outputToken: nextToken
      parameters:
        - in: query
          name: nextToken
          schema:
            type: string
          required: true
      responses:
        200:
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  nextToken:
                    type: string
```

In Smithy, until [custom vendor extensions can be rendered via traits](https://github.com/awslabs/smithy/pull/1609), you can add the `x-paginated` vendor extension via `smithyBuildOptions` in your `TypeSafeApiProject`, for example:

```python
new TypeSafeApiProject({
  model: {
    language: ModelLanguage.SMITHY,
    options: {
      smithy: {
        serviceName: {
          namespace: 'com.mycompany',
          serviceName: 'MyApi',
        },
        smithyBuildOptions: {
          projections: {
            openapi: {
              plugins: {
                openapi: {
                  jsonAdd: {
                    // Add the x-paginated vendor extension to the GET /pets operation
                    '/paths/~1pets/get/x-paginated': {
                      inputToken: 'nextToken',
                      outputToken: 'nextToken',
                    },
                  },
                },
              },
            },
          },
        },
      },
    },
  },
  ...
});
```

##### Custom QueryClient

If you wish to customise the react-query `QueryClient`, pass a custom instance to the client provider, eg:

```tsx
import { DefaultApiClientProvider } from "myapi-typescript-react-query-hooks";
import { QueryClient } from "@tanstack/react-query";

const queryClient = new QueryClient({ ... });

return (
  <DefaultApiClientProvider apiClient={api} client={queryClient}>
    {/* Components within the provider may make use of the hooks */}
  </DefaultApiClientProvider>
);
```

### Quick Start: Python

This guide assumes you want to write your CDK infrastructure in Python and your lambda handlers in Python, however note that you your infrastructure language and lambda handler language(s) are not tied to one another, you can mix and match as you like. Just specify the language in `runtime.languages` for any language you would like to write lambda handlers in.

#### Create Your API Project

Use the project in your `.projenrc.ts`. It can either be part of an [`nx-monorepo`](../nx-monorepo/README.md) (recommended) or used in a standalone fashion.

```python
import { NxMonorepoProject } from "@aws-prototyping-sdk/nx-monorepo";
import { TypeSafeApiProject } from "@aws-prototyping-sdk/type-safe-api";
import { AwsCdkTypeScriptApp } from "projen/lib/awscdk";
import { PythonProject } from "projen/lib/python";

// Create the monorepo
const monorepo = new NxMonorepoProject({
  name: "monorepo",
  defaultReleaseBranch: "main",
});

// Create the API project
const api = new TypeSafeApiProject({
  name: "myapi",
  parent: monorepo,
  outdir: "packages/api",
  // Smithy as the model language. You can also use ModelLanguage.OPENAPI
  model: {
    language: ModelLanguage.SMITHY,
    options: {
      smithy: {
        serviceName: {
          namespace: "com.mycompany",
          serviceName: "MyApi",
        },
      },
    },
  },
  // Generate client and server types in TypeScript, Python, and Java
  runtime: {
    languages: [Language.TYPESCRIPT, Language.PYTHON, Language.JAVA],
  },
  // Generate CDK infrastructure in Python
  infrastructure: {
    language: Language.PYTHON,
  },
  // Generate HTML documentation
  documentation: {
    formats: [DocumentationFormat.HTML_REDOC],
  },
});

// Create a project for our lambda handlers written in python
const lambdas = new PythonProject({
  name: "lambdas",
  parent: monorepo,
  outdir: "packages/lambdas",
  authorEmail: "me@example.com",
  authorName: "me",
  moduleName: "lambdas",
  version: "1.0.0",
  // Poetry is used to simplify local python dependencies
  poetry: true,
});

// Add a local dependency on the generated python runtime
monorepo.addPythonPoetryDependency(lambdas, api.runtime.python!);

// Add commands to the lambda project's package task to create a distributable which can be deployed to AWS Lambda
lambdas.packageTask.exec(`mkdir -p lambda-dist && rm -rf lambda-dist/*`);
lambdas.packageTask.exec(
  `cp -r ${lambdas.moduleName} lambda-dist/${lambdas.moduleName}`
);
lambdas.packageTask.exec(
  `poetry export --without-hashes --format=requirements.txt > lambda-dist/requirements.txt`
);
lambdas.packageTask.exec(
  `pip install -r lambda-dist/requirements.txt --target lambda-dist --upgrade`
);
lambdas.gitignore.addPatterns("lambda-dist");

// Create a CDK infrastructure project
const infra = new AwsCdkPythonApp({
  name: "infra",
  parent: monorepo,
  outdir: "packages/infra",
  authorEmail: "me@example.com",
  authorName: "me",
  cdkVersion: "2.0.0",
  moduleName: "infra",
  version: "1.0.0",
  poetry: true,
});

// The infrastructure project depends on the python types, python infrastructure, and the lambda package
monorepo.addPythonPoetryDependency(infra, api.runtime.python!);
monorepo.addPythonPoetryDependency(infra, api.infrastructure.python!);
monorepo.addPythonPoetryDependency(infra, lambdas);

monorepo.synth();
```

#### Use the CDK Construct

In your CDK application, consume the `Api` construct, vended from the generated Python infrastructure package.

```python
import os
from aws_cdk import Stack
from constructs import Construct
from aws_cdk.aws_lambda import LayerVersion, Code, Function, Runtime
from aws_prototyping_sdk.type_safe_api import Authorizers, TypeSafeApiIntegration, Integrations

from myapi_python_runtime.apis.tags.default_api_operation_config import OperationConfig
from myapi_python_infra.api import Api
from pathlib import Path
from os import path

class MyStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Use the generated Api construct
        self.api = Api(self, 'Api',
            default_authorizer=Authorizers.iam(),
            integrations=OperationConfig(
                say_hello=TypeSafeApiIntegration(
                    # Create a python lambda function from our "lambda-dist" package
                    integration=Integrations.lambda_(Function(self, 'SayHello',
                        runtime=Runtime.PYTHON_3_9,
                        code=Code.from_asset(path.join("..", "lambdas", "lambda-dist")),
                        handler="lambdas.say_hello.handler",
                    )),
                ),
            ),
        )
```

#### Implement a Lambda Handler

In your `lambdas` project you can define your lambda handler in its source directory, eg `lambdas/lambdas/say_hello.py`:

```python
from myapi_python_runtime.model.say_hello_response_content import SayHelloResponseContent
from myapi_python_runtime.apis.tags.default_api_operation_config import say_hello_handler,
    SayHelloRequest, SayHelloOperationResponses, ApiResponse


@say_hello_handler
def handler(input: SayHelloRequest, **kwargs) -> SayHelloOperationResponses:
    return ApiResponse(
        status_code=200,
        body=SayHelloResponseContent(message="Hello {}".format(input.request_parameters["name"])),
        headers={}
    )
```

### Quick Start: Java

This guide assumes you want to write your CDK infrastructure in Java and your lambda handlers in Java, however note that you your infrastructure language and lambda handler language(s) are not tied to one another, you can mix and match as you like.

#### Create Your API Project

Use the project in your `.projenrc.ts`. It can either be part of an [`nx-monorepo`](../nx-monorepo/README.md) (recommended) or used in a standalone fashion.

```python
import { NxMonorepoProject } from "@aws-prototyping-sdk/nx-monorepo";
import { TypeSafeApiProject } from "@aws-prototyping-sdk/type-safe-api";
import { AwsCdkTypeScriptApp } from "projen/lib/awscdk";
import { JavaProject } from "projen/lib/java";

// Create the monorepo
const monorepo = new NxMonorepoProject({
  name: "monorepo",
  defaultReleaseBranch: "main",
});

// Create the API project
const api = new TypeSafeApiProject({
  name: "myapi",
  parent: monorepo,
  outdir: "packages/api",
  // Smithy as the model language. You can also use ModelLanguage.OPENAPI
  model: {
    language: ModelLanguage.SMITHY,
    options: {
      smithy: {
        serviceName: {
          namespace: "com.mycompany",
          serviceName: "MyApi",
        },
      },
    },
  },
  // Generate client and server types in TypeScript, Python and Java
  runtime: {
    languages: [Language.TYPESCRIPT, Language.PYTHON, Language.JAVA],
  },
  // Generate CDK infrastructure in Java
  infrastructure: {
    language: Language.JAVA,
  },
  // Generate HTML documentation
  documentation: {
    formats: [DocumentationFormat.HTML_REDOC],
  },
});

const lambdas = new JavaProject({
  name: "lambdas",
  parent: monorepo,
  outdir: "packages/lambdas",
  artifactId: "lambdas",
  groupId: "com.my.api",
  version: "1.0.0",
});

// The lambdas package needs a dependency on the generated java runtime
monorepo.addJavaDependency(lambdas, api.runtime.java!);

// Use the maven shade plugin to build a "super jar" which we can deploy to AWS Lambda
lambdas.pom.addPlugin("org.apache.maven.plugins/maven-shade-plugin@3.3.0", {
  configuration: {
    createDependencyReducedPom: false,
  },
  executions: [
    {
      id: "shade-task",
      phase: "package",
      goals: ["shade"],
    },
  ],
});

const infra = new AwsCdkJavaApp({
  name: "infra",
  parent: monorepo,
  outdir: "packages/infra",
  artifactId: "infra",
  groupId: "com.my.api",
  mainClass: "com.my.api.MyApp",
  version: "1.0.0",
  cdkVersion: "2.0.0",
});

// Add a dependency on the generated CDK infrastructure
monorepo.addJavaDependency(infra, api.infrastructure.java!);

// Make sure the java lambda builds before our CDK infra
monorepo.addImplicitDependency(infra, lambdas);

monorepo.synth();
```

#### Use the CDK Construct

In your CDK application, consume the `Api` construct, vended from the generated Java infrastructure package.

```java
package com.my.api;

import com.generated.api.myapijavainfra.infra.Api;
import com.generated.api.myapijavainfra.infra.ApiProps;
import com.generated.api.myapijavaruntime.runtime.api.OperationConfig;

import software.amazon.awscdk.Duration;
import software.amazon.awscdk.services.apigateway.CorsOptions;
import software.amazon.awscdk.services.lambda.Code;
import software.amazon.awscdk.services.lambda.Function;
import software.amazon.awscdk.services.lambda.FunctionProps;
import software.amazon.awscdk.services.lambda.Runtime;
import software.aws.awsprototypingsdk.typesafeapi.Authorizers;
import software.aws.awsprototypingsdk.typesafeapi.Integrations;
import software.aws.awsprototypingsdk.typesafeapi.TypeSafeApiIntegration;

import software.amazon.awscdk.App;
import software.amazon.awscdk.Stack;

import java.util.Arrays;

public class MyApp {
    public static void main(final String[] args) {
        App app = new App();
        Stack s = new Stack(app, "infra");

        // Declare the API construct to deploy the API Gateway resources
        new Api(s, "Api", ApiProps.builder()
                .defaultAuthorizer(Authorizers.iam())
                .corsOptions(CorsOptions.builder()
                        .allowOrigins(Arrays.asList("*"))
                        .allowMethods(Arrays.asList("*"))
                        .build())
                .integrations(OperationConfig.<TypeSafeApiIntegration>builder()
                        .sayHello(TypeSafeApiIntegration.builder()
                                .integration(Integrations.lambda(
                                        // Point the lambda function to our built jar from the "lambdas" package
                                        new Function(s, "say-hello", FunctionProps.builder()
                                                .code(Code.fromAsset("../lambdas/dist/java/com/my/api/lambdas/1.0.0/lambdas-1.0.0.jar"))
                                                .handler("com.my.api.SayHelloHandler")
                                                .runtime(Runtime.JAVA_11)
                                                .timeout(Duration.seconds(30))
                                                .build())))
                                .build())
                        .build())
                .build());

        app.synth();
    }
}
```

#### Implement a Lambda Handler

In your `lambdas` project you can define your lambda handler in its source directory, eg `lambdas/src/main/java/com/my/api/SayHelloHandler.java`:

```java
package com.my.api;

import com.generated.api.myapijavaruntime.runtime.api.Handlers.SayHello;
import com.generated.api.myapijavaruntime.runtime.api.Handlers.SayHello200Response;
import com.generated.api.myapijavaruntime.runtime.api.Handlers.SayHelloRequestInput;
import com.generated.api.myapijavaruntime.runtime.api.Handlers.SayHelloResponse;
import com.generated.api.myapijavaruntime.runtime.model.SayHelloResponseContent;

/**
 * An example lambda handler which uses the generated handler wrapper class (Handlers.SayHello) to manage marshalling
 * inputs and outputs.
 */
public class SayHelloHandler extends SayHello {
    @Override
    public SayHelloResponse handle(SayHelloRequestInput sayHelloRequestInput) {
        return SayHello200Response.of(SayHelloResponseContent.builder()
                .message(String.format("Hello %s", sayHelloRequestInput.getInput().getRequestParameters().getName()))
                .build());
    }
}

```

### Other Details

#### Customising Generated Types/Infrastructure Projects

By default, the generated types and infrastructure projects are configured automatically, including their project names. You can customise the generated projects using the `runtime.options.<language>` or `infrastructure.options.<language>` properties when constructing the `TypeSafeApiProject`.

#### AWS WAFv2 Web ACL

By default, a [Web ACL](https://docs.aws.amazon.com/waf/latest/developerguide/web-acl.html) is deployed and attached to your API Gateway Rest API with the "[AWSManagedRulesCommonRuleSet](https://docs.aws.amazon.com/waf/latest/developerguide/aws-managed-rule-groups-baseline.html)", which provides protection against exploitation of a wide range of vulnerabilities, including some of the high risk and commonly occurring vulnerabilities described in OWASP publications such as [OWASP Top 10](https://owasp.org/www-project-top-ten/).

You can customise the Web ACL configuration via the `webAclOptions` of your `Api` CDK construct, eg:

```python
export class SampleApi extends Api {
  constructor(scope: Construct, id: string) {
    super(scope, id, {
      integrations: { ... },
      webAclOptions: {
        // Allow access only to specific CIDR ranges
        cidrAllowList: {
          cidrType: 'IPV4',
          cidrRanges: ['1.2.3.4/5'],
        },
        // Pick from the set here: https://docs.aws.amazon.com/waf/latest/developerguide/aws-managed-rule-groups-list.html
        managedRules: [
          { vendor: 'AWS', name: 'AWSManagedRulesSQLiRuleSet' },
        ],
      },
    });
  }
}
```

You can remove the Web ACL entirely with `webAclOptions: { disable: true }` - you may wish to use this if you'd like to set up a Web ACL yourself with more control over the rules.

#### Smithy IntelliJ Plugin

The Smithy-based projects are compatible with the [Smithy IntelliJ Plugin](https://github.com/iancaffey/smithy-intellij-plugin), which provides syntax highlighting and auto-complete for your Smithy model. To make use of it, perform the following steps:

* Install the "Smithy" plugin (under `Preferences -> Plugins`)
* Right-click on the `smithy/build.gradle` file in your Smithy API project
* Select "Link Gradle Project"

#### Tagging Operations

Operations can be grouped together into logical collections via tags. This can be achieved in Smithy with the `@tags` trait:

```smithy
@tags(["pets", "users"])
operation PurchasePet {
  ...
}
```

Or in OpenAPI using the `tags` property:

```yaml
paths:
  /pets/purchase:
    post:
      operationId: purchasePet
      tags:
        - pets
        - users
      ...
```

When multiple tags are used, the "first" tag is considered to be the API that the operation belongs to, so in the generated client, the above example operation would be included in the `PetsApi` client but not the `UsersApi` client.

Multiple tags are still useful for documentation generation, for example `DocumentationFormat.HTML_REDOC` will group operations by tag in the side navigation bar.

If you would like to introduce tags without breaking existing clients, we recommend first adding a tag named `default` to all operations.

⚠️ **Important Note**: Smithy versions below `1.28.0` sort tags in alphabetical order and so the "first" tag will be the earliest in the alphabet. Therefore, if using tags with older versions of Smithy, we recommend prefixing your desired first tag with an underscore (for example `_default`). This is rectified in `1.28.0`, where tag order from the `@tags` trait is preserved.

#### Smithy Model Libraries and Dependencies

You can instantiate the TypeSafeApiModelProject on its own to create a standalone Smithy model library.

You can consume the library using the `addSmithyDeps` method, which adds a local file dependency on the built Smithy jar.

```python
// Standalone model project, used as our model library
const shapes = new TypeSafeApiModelProject({
  name: "shapes",
  parent: monorepo,
  outdir: "packages/shapes",
  modelLanguage: ModelLanguage.SMITHY,
  modelOptions: {
    smithy: {
      serviceName: {
        namespace: "com.my.shared.shapes",
        serviceName: "Ignored",
      },
    },
  },
});

const api = new TypeSafeApiProject({ ... });

// Add the implicit monorepo dependency (if using the nx-monorepo) to ensure the shape library is built before the api model
monorepo.addImplicitDependency(api.model, shapes);

// Add a local file dependency on the built shapes jar
api.model.smithy!.addSmithyDeps(shapes.smithy!);
```

#### Local API Development Server

You can use the [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) to run a local development server for your API. You can achieve this using the following steps:

1. Synthesize your CDK stack containing your `Api` construct (this might be your `AwsCdkTypeScriptApp` project for example), with the context property `type-safe-api-local` set to `true`, for example:

```bash
cd packages/infra
npx cdk synth --context type-safe-api-local=true
```

1. Use the AWS SAM CLI to start the local development server, pointing it at the cloudformation template synthesized from the above command (note that the command will fail if docker is not running)

```bash
sam local start-api -t cdk.out/<your-stack>.template.json
```

You will need to repeat the above steps every time you make a code change for them to be reflected in your local development server.

See the [AWS SAM CLI Reference](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-local-start-api.html) for more information on the commands to run.

Make sure you do not deploy your CDK stack with `type-safe-api-local` set to `true`, since this uses an inline API definition which bloats the CloudFormation template and can exceed the maximum template size depending on the size of your API.

##### Limitations

Note that there is currently a limitation with SAM CLI where it does not support mock integrations, which means that the development server will not respond to OPTIONS requests even if you specified `corsOptions: { ... }` in your `Api` construct. This is being tracked as a [feature request here](https://github.com/aws/aws-sam-cli/issues/4973).

Note also that your API business logic may include operations which do not work locally, or may interact with real AWS resources depending on the AWS credentials you start your local development server with.
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from ._jsii import *

import aws_cdk.aws_apigateway as _aws_cdk_aws_apigateway_ceddda9d
import aws_cdk.aws_cognito as _aws_cdk_aws_cognito_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_wafv2 as _aws_cdk_aws_wafv2_ceddda9d
import constructs as _constructs_77d1e7e8
import projen as _projen_04054675
import projen.java as _projen_java_04054675
import projen.python as _projen_python_04054675
import projen.typescript as _projen_typescript_04054675


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.ApiGatewayIntegration",
    jsii_struct_bases=[],
    name_mapping={
        "cache_key_parameters": "cacheKeyParameters",
        "cache_namespace": "cacheNamespace",
        "connection_id": "connectionId",
        "connection_type": "connectionType",
        "content_handling": "contentHandling",
        "credentials": "credentials",
        "http_method": "httpMethod",
        "passthrough_behavior": "passthroughBehavior",
        "request_parameters": "requestParameters",
        "request_templates": "requestTemplates",
        "responses": "responses",
        "timeout_in_millis": "timeoutInMillis",
        "tls_config": "tlsConfig",
        "type": "type",
        "uri": "uri",
    },
)
class ApiGatewayIntegration:
    def __init__(
        self,
        *,
        cache_key_parameters: typing.Optional[typing.Sequence[builtins.str]] = None,
        cache_namespace: typing.Optional[builtins.str] = None,
        connection_id: typing.Optional[builtins.str] = None,
        connection_type: typing.Optional[builtins.str] = None,
        content_handling: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[builtins.str] = None,
        http_method: typing.Optional[builtins.str] = None,
        passthrough_behavior: typing.Optional[builtins.str] = None,
        request_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        request_templates: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        responses: typing.Optional[typing.Mapping[builtins.str, typing.Union["ApiGatewayIntegrationResponse", typing.Dict[builtins.str, typing.Any]]]] = None,
        timeout_in_millis: typing.Optional[jsii.Number] = None,
        tls_config: typing.Optional[typing.Union["ApiGatewayIntegrationTlsConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        type: typing.Optional[builtins.str] = None,
        uri: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Represents an api gateway integration.

        :param cache_key_parameters: (experimental) A list of request parameters whose values are to be cached.
        :param cache_namespace: (experimental) An API-specific tag group of related cached parameters.
        :param connection_id: (experimental) The ID of a VpcLink for the private integration.
        :param connection_type: (experimental) The integration connection type. The valid value is "VPC_LINK" for private integration or "INTERNET", otherwise.
        :param content_handling: (experimental) Request payload encoding conversion types. Valid values are 1) CONVERT_TO_TEXT, for converting a binary payload into a base64-encoded string or converting a text payload into a utf-8-encoded string or passing through the text payload natively without modification, and 2) CONVERT_TO_BINARY, for converting a text payload into a base64-decoded blob or passing through a binary payload natively without modification.
        :param credentials: (experimental) For AWS IAM role-based credentials, specify the ARN of an appropriate IAM role. If unspecified, credentials default to resource-based permissions that must be added manually to allow the API to access the resource. For more information, see Granting Permissions Using a Resource Policy. Note: When using IAM credentials, make sure that AWS STS Regional endpoints are enabled for the Region where this API is deployed for best performance.
        :param http_method: (experimental) The HTTP method used in the integration request. For Lambda function invocations, the value must be POST.
        :param passthrough_behavior: (experimental) Specifies how a request payload of unmapped content type is passed through the integration request without modification. Supported values are when_no_templates, when_no_match, and never.
        :param request_parameters: (experimental) Specifies mappings from method request parameters to integration request parameters. Supported request parameters are querystring, path, header, and body.
        :param request_templates: (experimental) Mapping templates for a request payload of specified MIME types.
        :param responses: (experimental) Defines the method's responses and specifies desired parameter mappings or payload mappings from integration responses to method responses.
        :param timeout_in_millis: (experimental) Custom timeout between 50 and 29,000 milliseconds. The default value is 29,000 milliseconds or 29 seconds.
        :param tls_config: (experimental) Specifies the TLS configuration for an integration.
        :param type: (experimental) The type of integration with the specified backend.
        :param uri: (experimental) The endpoint URI of the backend. For integrations of the aws type, this is an ARN value. For the HTTP integration, this is the URL of the HTTP endpoint including the https or http scheme.

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-swagger-extensions-integration.html
        :stability: experimental
        '''
        if isinstance(tls_config, dict):
            tls_config = ApiGatewayIntegrationTlsConfig(**tls_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54bbaf1f62ed65563fa5fe86f006bb219a4165e70e8954489c0c8a57eb786208)
            check_type(argname="argument cache_key_parameters", value=cache_key_parameters, expected_type=type_hints["cache_key_parameters"])
            check_type(argname="argument cache_namespace", value=cache_namespace, expected_type=type_hints["cache_namespace"])
            check_type(argname="argument connection_id", value=connection_id, expected_type=type_hints["connection_id"])
            check_type(argname="argument connection_type", value=connection_type, expected_type=type_hints["connection_type"])
            check_type(argname="argument content_handling", value=content_handling, expected_type=type_hints["content_handling"])
            check_type(argname="argument credentials", value=credentials, expected_type=type_hints["credentials"])
            check_type(argname="argument http_method", value=http_method, expected_type=type_hints["http_method"])
            check_type(argname="argument passthrough_behavior", value=passthrough_behavior, expected_type=type_hints["passthrough_behavior"])
            check_type(argname="argument request_parameters", value=request_parameters, expected_type=type_hints["request_parameters"])
            check_type(argname="argument request_templates", value=request_templates, expected_type=type_hints["request_templates"])
            check_type(argname="argument responses", value=responses, expected_type=type_hints["responses"])
            check_type(argname="argument timeout_in_millis", value=timeout_in_millis, expected_type=type_hints["timeout_in_millis"])
            check_type(argname="argument tls_config", value=tls_config, expected_type=type_hints["tls_config"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument uri", value=uri, expected_type=type_hints["uri"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cache_key_parameters is not None:
            self._values["cache_key_parameters"] = cache_key_parameters
        if cache_namespace is not None:
            self._values["cache_namespace"] = cache_namespace
        if connection_id is not None:
            self._values["connection_id"] = connection_id
        if connection_type is not None:
            self._values["connection_type"] = connection_type
        if content_handling is not None:
            self._values["content_handling"] = content_handling
        if credentials is not None:
            self._values["credentials"] = credentials
        if http_method is not None:
            self._values["http_method"] = http_method
        if passthrough_behavior is not None:
            self._values["passthrough_behavior"] = passthrough_behavior
        if request_parameters is not None:
            self._values["request_parameters"] = request_parameters
        if request_templates is not None:
            self._values["request_templates"] = request_templates
        if responses is not None:
            self._values["responses"] = responses
        if timeout_in_millis is not None:
            self._values["timeout_in_millis"] = timeout_in_millis
        if tls_config is not None:
            self._values["tls_config"] = tls_config
        if type is not None:
            self._values["type"] = type
        if uri is not None:
            self._values["uri"] = uri

    @builtins.property
    def cache_key_parameters(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of request parameters whose values are to be cached.

        :stability: experimental
        '''
        result = self._values.get("cache_key_parameters")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cache_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) An API-specific tag group of related cached parameters.

        :stability: experimental
        '''
        result = self._values.get("cache_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connection_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ID of a VpcLink for the private integration.

        :see: https://docs.aws.amazon.com/apigateway/latest/api/API_VpcLink.html
        :stability: experimental
        '''
        result = self._values.get("connection_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connection_type(self) -> typing.Optional[builtins.str]:
        '''(experimental) The integration connection type.

        The valid value is "VPC_LINK" for private integration or "INTERNET", otherwise.

        :stability: experimental
        '''
        result = self._values.get("connection_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def content_handling(self) -> typing.Optional[builtins.str]:
        '''(experimental) Request payload encoding conversion types.

        Valid values are 1) CONVERT_TO_TEXT, for converting a binary payload
        into a base64-encoded string or converting a text payload into a utf-8-encoded string or passing through the text
        payload natively without modification, and 2) CONVERT_TO_BINARY, for converting a text payload into a
        base64-decoded blob or passing through a binary payload natively without modification.

        :stability: experimental
        '''
        result = self._values.get("content_handling")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def credentials(self) -> typing.Optional[builtins.str]:
        '''(experimental) For AWS IAM role-based credentials, specify the ARN of an appropriate IAM role.

        If unspecified, credentials default
        to resource-based permissions that must be added manually to allow the API to access the resource. For more
        information, see Granting Permissions Using a Resource Policy.

        Note: When using IAM credentials, make sure that AWS STS Regional endpoints are enabled for the Region where this
        API is deployed for best performance.

        :stability: experimental
        '''
        result = self._values.get("credentials")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def http_method(self) -> typing.Optional[builtins.str]:
        '''(experimental) The HTTP method used in the integration request.

        For Lambda function invocations, the value must be POST.

        :stability: experimental
        '''
        result = self._values.get("http_method")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def passthrough_behavior(self) -> typing.Optional[builtins.str]:
        '''(experimental) Specifies how a request payload of unmapped content type is passed through the integration request without modification.

        Supported values are when_no_templates, when_no_match, and never.

        :see: https://docs.aws.amazon.com/apigateway/latest/api/API_Integration.html#passthroughBehavior
        :stability: experimental
        '''
        result = self._values.get("passthrough_behavior")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def request_parameters(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Specifies mappings from method request parameters to integration request parameters.

        Supported request parameters
        are querystring, path, header, and body.

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-swagger-extensions-integration-requestParameters.html
        :stability: experimental
        '''
        result = self._values.get("request_parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def request_templates(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Mapping templates for a request payload of specified MIME types.

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-swagger-extensions-integration-requestTemplates.html
        :stability: experimental
        '''
        result = self._values.get("request_templates")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def responses(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, "ApiGatewayIntegrationResponse"]]:
        '''(experimental) Defines the method's responses and specifies desired parameter mappings or payload mappings from integration responses to method responses.

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-swagger-extensions-integration-responses.html
        :stability: experimental
        '''
        result = self._values.get("responses")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, "ApiGatewayIntegrationResponse"]], result)

    @builtins.property
    def timeout_in_millis(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Custom timeout between 50 and 29,000 milliseconds.

        The default value is 29,000 milliseconds or 29 seconds.

        :stability: experimental
        '''
        result = self._values.get("timeout_in_millis")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tls_config(self) -> typing.Optional["ApiGatewayIntegrationTlsConfig"]:
        '''(experimental) Specifies the TLS configuration for an integration.

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-extensions-integration-tls-config.html
        :stability: experimental
        '''
        result = self._values.get("tls_config")
        return typing.cast(typing.Optional["ApiGatewayIntegrationTlsConfig"], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''(experimental) The type of integration with the specified backend.

        :see: https://docs.aws.amazon.com/apigateway/latest/api/API_Integration.html#type
        :stability: experimental
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uri(self) -> typing.Optional[builtins.str]:
        '''(experimental) The endpoint URI of the backend.

        For integrations of the aws type, this is an ARN value.
        For the HTTP integration, this is the URL of the HTTP endpoint including the https or http scheme.

        :stability: experimental
        '''
        result = self._values.get("uri")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayIntegration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.ApiGatewayIntegrationResponse",
    jsii_struct_bases=[],
    name_mapping={
        "response_parameters": "responseParameters",
        "response_templates": "responseTemplates",
        "status_code": "statusCode",
        "content_handling": "contentHandling",
    },
)
class ApiGatewayIntegrationResponse:
    def __init__(
        self,
        *,
        response_parameters: typing.Mapping[builtins.str, builtins.str],
        response_templates: typing.Mapping[builtins.str, builtins.str],
        status_code: builtins.str,
        content_handling: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) API Gateway integration response.

        :param response_parameters: (experimental) Specifies parameter mappings for the response.
        :param response_templates: (experimental) Specifies MIME type-specific mapping templates for the response’s payload.
        :param status_code: (experimental) HTTP status code for the method response.
        :param content_handling: (experimental) Response payload encoding conversion types. Valid values are 1) CONVERT_TO_TEXT, for converting a binary payload into a base64-encoded string or converting a text payload into a utf-8-encoded string or passing through the text payload natively without modification, and 2) CONVERT_TO_BINARY, for converting a text payload into a base64-decoded blob or passing through a binary payload natively without modification.

        :see: https://docs.aws.amazon.com/apigateway/latest/api/API_Integration.html
        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac85c5045c3a1b7e5fa301a20c8e42758a5987c59645f4aa7d181d4e3c67f689)
            check_type(argname="argument response_parameters", value=response_parameters, expected_type=type_hints["response_parameters"])
            check_type(argname="argument response_templates", value=response_templates, expected_type=type_hints["response_templates"])
            check_type(argname="argument status_code", value=status_code, expected_type=type_hints["status_code"])
            check_type(argname="argument content_handling", value=content_handling, expected_type=type_hints["content_handling"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "response_parameters": response_parameters,
            "response_templates": response_templates,
            "status_code": status_code,
        }
        if content_handling is not None:
            self._values["content_handling"] = content_handling

    @builtins.property
    def response_parameters(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''(experimental) Specifies parameter mappings for the response.

        :stability: experimental
        '''
        result = self._values.get("response_parameters")
        assert result is not None, "Required property 'response_parameters' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    @builtins.property
    def response_templates(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''(experimental) Specifies MIME type-specific mapping templates for the response’s payload.

        :stability: experimental
        '''
        result = self._values.get("response_templates")
        assert result is not None, "Required property 'response_templates' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    @builtins.property
    def status_code(self) -> builtins.str:
        '''(experimental) HTTP status code for the method response.

        :stability: experimental
        '''
        result = self._values.get("status_code")
        assert result is not None, "Required property 'status_code' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def content_handling(self) -> typing.Optional[builtins.str]:
        '''(experimental) Response payload encoding conversion types.

        Valid values are 1) CONVERT_TO_TEXT, for converting a binary payload
        into a base64-encoded string or converting a text payload into a utf-8-encoded string or passing through the text
        payload natively without modification, and 2) CONVERT_TO_BINARY, for converting a text payload into a
        base64-decoded blob or passing through a binary payload natively without modification.

        :stability: experimental
        '''
        result = self._values.get("content_handling")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayIntegrationResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.ApiGatewayIntegrationTlsConfig",
    jsii_struct_bases=[],
    name_mapping={"insecure_skip_verification": "insecureSkipVerification"},
)
class ApiGatewayIntegrationTlsConfig:
    def __init__(
        self,
        *,
        insecure_skip_verification: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Specifies the TLS configuration for an integration.

        :param insecure_skip_verification: (experimental) Specifies whether or not API Gateway skips verification that the certificate for an integration endpoint is issued by a supported certificate authority. This isn’t recommended, but it enables you to use certificates that are signed by private certificate authorities, or certificates that are self-signed. If enabled, API Gateway still performs basic certificate validation, which includes checking the certificate's expiration date, hostname, and presence of a root certificate authority. Supported only for HTTP and HTTP_PROXY integrations.

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-extensions-integration-tls-config.html
        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13da332b7a7dcdfb32928a99f0c6dc04a61d0d2e03fed3b12937ae3d342aea5b)
            check_type(argname="argument insecure_skip_verification", value=insecure_skip_verification, expected_type=type_hints["insecure_skip_verification"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if insecure_skip_verification is not None:
            self._values["insecure_skip_verification"] = insecure_skip_verification

    @builtins.property
    def insecure_skip_verification(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Specifies whether or not API Gateway skips verification that the certificate for an integration endpoint is issued by a supported certificate authority.

        This isn’t recommended, but it enables you to use certificates that are
        signed by private certificate authorities, or certificates that are self-signed. If enabled, API Gateway still
        performs basic certificate validation, which includes checking the certificate's expiration date, hostname, and
        presence of a root certificate authority. Supported only for HTTP and HTTP_PROXY integrations.

        :stability: experimental
        '''
        result = self._values.get("insecure_skip_verification")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayIntegrationTlsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Authorizer(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-prototyping-sdk/type-safe-api.Authorizer",
):
    '''(experimental) An authorizer for authorizing API requests.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        authorization_type: _aws_cdk_aws_apigateway_ceddda9d.AuthorizationType,
        authorizer_id: builtins.str,
        authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param authorization_type: (experimental) The type of the authorizer.
        :param authorizer_id: (experimental) The unique identifier for the authorizer.
        :param authorization_scopes: (experimental) Scopes for the authorizer, if any.

        :stability: experimental
        '''
        props = AuthorizerProps(
            authorization_type=authorization_type,
            authorizer_id=authorizer_id,
            authorization_scopes=authorization_scopes,
        )

        jsii.create(self.__class__, self, [props])

    @builtins.property
    @jsii.member(jsii_name="authorizationType")
    def authorization_type(self) -> _aws_cdk_aws_apigateway_ceddda9d.AuthorizationType:
        '''(experimental) The type of the authorizer.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.AuthorizationType, jsii.get(self, "authorizationType"))

    @builtins.property
    @jsii.member(jsii_name="authorizerId")
    def authorizer_id(self) -> builtins.str:
        '''(experimental) The unique identifier for the authorizer.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "authorizerId"))

    @builtins.property
    @jsii.member(jsii_name="authorizationScopes")
    def authorization_scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Scopes for the authorizer, if any.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "authorizationScopes"))


class _AuthorizerProxy(Authorizer):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, Authorizer).__jsii_proxy_class__ = lambda : _AuthorizerProxy


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.AuthorizerProps",
    jsii_struct_bases=[],
    name_mapping={
        "authorization_type": "authorizationType",
        "authorizer_id": "authorizerId",
        "authorization_scopes": "authorizationScopes",
    },
)
class AuthorizerProps:
    def __init__(
        self,
        *,
        authorization_type: _aws_cdk_aws_apigateway_ceddda9d.AuthorizationType,
        authorizer_id: builtins.str,
        authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Properties for an authorizer.

        :param authorization_type: (experimental) The type of the authorizer.
        :param authorizer_id: (experimental) The unique identifier for the authorizer.
        :param authorization_scopes: (experimental) Scopes for the authorizer, if any.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a0b3bb1dc7df594503f85f7e4e203386d8288de3b7e59c33559a1bce31752f5)
            check_type(argname="argument authorization_type", value=authorization_type, expected_type=type_hints["authorization_type"])
            check_type(argname="argument authorizer_id", value=authorizer_id, expected_type=type_hints["authorizer_id"])
            check_type(argname="argument authorization_scopes", value=authorization_scopes, expected_type=type_hints["authorization_scopes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "authorization_type": authorization_type,
            "authorizer_id": authorizer_id,
        }
        if authorization_scopes is not None:
            self._values["authorization_scopes"] = authorization_scopes

    @builtins.property
    def authorization_type(self) -> _aws_cdk_aws_apigateway_ceddda9d.AuthorizationType:
        '''(experimental) The type of the authorizer.

        :stability: experimental
        '''
        result = self._values.get("authorization_type")
        assert result is not None, "Required property 'authorization_type' is missing"
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.AuthorizationType, result)

    @builtins.property
    def authorizer_id(self) -> builtins.str:
        '''(experimental) The unique identifier for the authorizer.

        :stability: experimental
        '''
        result = self._values.get("authorizer_id")
        assert result is not None, "Required property 'authorizer_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authorization_scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Scopes for the authorizer, if any.

        :stability: experimental
        '''
        result = self._values.get("authorization_scopes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthorizerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Authorizers(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-prototyping-sdk/type-safe-api.Authorizers",
):
    '''(experimental) Class used to construct authorizers for use in the OpenApiGatewayLambdaApi construct.

    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="cognito")
    @builtins.classmethod
    def cognito(
        cls,
        *,
        authorizer_id: builtins.str,
        user_pools: typing.Sequence[_aws_cdk_aws_cognito_ceddda9d.IUserPool],
        authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> "CognitoAuthorizer":
        '''(experimental) A Cognito User Pools authorizer.

        :param authorizer_id: (experimental) Unique identifier for this authorizer.
        :param user_pools: (experimental) The Cognito user pools associated with this authorizer.
        :param authorization_scopes: (experimental) A list of authorization scopes configured on the method. When used as the default authorizer, these scopes will be applied to all methods without an authorizer at the integration level. Default: []

        :stability: experimental
        '''
        props = CognitoAuthorizerProps(
            authorizer_id=authorizer_id,
            user_pools=user_pools,
            authorization_scopes=authorization_scopes,
        )

        return typing.cast("CognitoAuthorizer", jsii.sinvoke(cls, "cognito", [props]))

    @jsii.member(jsii_name="custom")
    @builtins.classmethod
    def custom(
        cls,
        *,
        authorizer_id: builtins.str,
        function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        authorizer_result_ttl_in_seconds: typing.Optional[jsii.Number] = None,
        identity_source: typing.Optional[builtins.str] = None,
        type: typing.Optional["CustomAuthorizerType"] = None,
    ) -> "CustomAuthorizer":
        '''(experimental) A custom authorizer.

        :param authorizer_id: (experimental) Unique identifier for this authorizer.
        :param function: (experimental) The lambda function used to authorize requests.
        :param authorizer_result_ttl_in_seconds: (experimental) The number of seconds during which the authorizer result is cached. Default: 300
        :param identity_source: (experimental) The source of the identity in an incoming request. Default: "method.request.header.Authorization"
        :param type: (experimental) The type of custom authorizer. Default: CustomAuthorizerType.TOKEN

        :stability: experimental
        '''
        props = CustomAuthorizerProps(
            authorizer_id=authorizer_id,
            function=function,
            authorizer_result_ttl_in_seconds=authorizer_result_ttl_in_seconds,
            identity_source=identity_source,
            type=type,
        )

        return typing.cast("CustomAuthorizer", jsii.sinvoke(cls, "custom", [props]))

    @jsii.member(jsii_name="iam")
    @builtins.classmethod
    def iam(cls) -> "IamAuthorizer":
        '''(experimental) An IAM authorizer which uses AWS signature version 4 to authorize requests.

        :stability: experimental
        '''
        return typing.cast("IamAuthorizer", jsii.sinvoke(cls, "iam", []))

    @jsii.member(jsii_name="none")
    @builtins.classmethod
    def none(cls) -> "NoneAuthorizer":
        '''(experimental) No authorizer.

        :stability: experimental
        '''
        return typing.cast("NoneAuthorizer", jsii.sinvoke(cls, "none", []))


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.CidrAllowList",
    jsii_struct_bases=[],
    name_mapping={"cidr_ranges": "cidrRanges", "cidr_type": "cidrType"},
)
class CidrAllowList:
    def __init__(
        self,
        *,
        cidr_ranges: typing.Sequence[builtins.str],
        cidr_type: builtins.str,
    ) -> None:
        '''(experimental) Representation of a CIDR range.

        :param cidr_ranges: (experimental) Specify an IPv4 address by using CIDR notation. For example: To configure AWS WAF to allow, block, or count requests that originated from the IP address 192.0.2.44, specify 192.0.2.44/32 . To configure AWS WAF to allow, block, or count requests that originated from IP addresses from 192.0.2.0 to 192.0.2.255, specify 192.0.2.0/24 . For more information about CIDR notation, see the Wikipedia entry Classless Inter-Domain Routing . Specify an IPv6 address by using CIDR notation. For example: To configure AWS WAF to allow, block, or count requests that originated from the IP address 1111:0000:0000:0000:0000:0000:0000:0111, specify 1111:0000:0000:0000:0000:0000:0000:0111/128 . To configure AWS WAF to allow, block, or count requests that originated from IP addresses 1111:0000:0000:0000:0000:0000:0000:0000 to 1111:0000:0000:0000:ffff:ffff:ffff:ffff, specify 1111:0000:0000:0000:0000:0000:0000:0000/64 .
        :param cidr_type: (experimental) Type of CIDR range.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97fa5bbc32d6acfd09f204cad081dd902df873b5c29715c0f84e02901c4e9832)
            check_type(argname="argument cidr_ranges", value=cidr_ranges, expected_type=type_hints["cidr_ranges"])
            check_type(argname="argument cidr_type", value=cidr_type, expected_type=type_hints["cidr_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cidr_ranges": cidr_ranges,
            "cidr_type": cidr_type,
        }

    @builtins.property
    def cidr_ranges(self) -> typing.List[builtins.str]:
        '''(experimental) Specify an IPv4 address by using CIDR notation.

        For example:
        To configure AWS WAF to allow, block, or count requests that originated from the IP address 192.0.2.44, specify 192.0.2.44/32 .
        To configure AWS WAF to allow, block, or count requests that originated from IP addresses from 192.0.2.0 to 192.0.2.255, specify 192.0.2.0/24 .

        For more information about CIDR notation, see the Wikipedia entry Classless Inter-Domain Routing .

        Specify an IPv6 address by using CIDR notation. For example:
        To configure AWS WAF to allow, block, or count requests that originated from the IP address 1111:0000:0000:0000:0000:0000:0000:0111, specify 1111:0000:0000:0000:0000:0000:0000:0111/128 .
        To configure AWS WAF to allow, block, or count requests that originated from IP addresses 1111:0000:0000:0000:0000:0000:0000:0000 to 1111:0000:0000:0000:ffff:ffff:ffff:ffff, specify 1111:0000:0000:0000:0000:0000:0000:0000/64 .

        :stability: experimental
        '''
        result = self._values.get("cidr_ranges")
        assert result is not None, "Required property 'cidr_ranges' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def cidr_type(self) -> builtins.str:
        '''(experimental) Type of CIDR range.

        :stability: experimental
        '''
        result = self._values.get("cidr_type")
        assert result is not None, "Required property 'cidr_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CidrAllowList(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CognitoAuthorizer(
    Authorizer,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-prototyping-sdk/type-safe-api.CognitoAuthorizer",
):
    '''(experimental) An authorizer that uses Cognito identity or access tokens.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        authorizer_id: builtins.str,
        user_pools: typing.Sequence[_aws_cdk_aws_cognito_ceddda9d.IUserPool],
        authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param authorizer_id: (experimental) Unique identifier for this authorizer.
        :param user_pools: (experimental) The Cognito user pools associated with this authorizer.
        :param authorization_scopes: (experimental) A list of authorization scopes configured on the method. When used as the default authorizer, these scopes will be applied to all methods without an authorizer at the integration level. Default: []

        :stability: experimental
        '''
        props = CognitoAuthorizerProps(
            authorizer_id=authorizer_id,
            user_pools=user_pools,
            authorization_scopes=authorization_scopes,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="withScopes")
    def with_scopes(self, *authorization_scopes: builtins.str) -> "CognitoAuthorizer":
        '''(experimental) Returns this authorizer with scopes applied, intended for usage in individual operations where scopes may differ on a per-operation basis.

        :param authorization_scopes: the scopes to apply.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html#cfn-apigateway-method-authorizationscopes
        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51ad75e89d4fbd5ec94d8c79816220551ccdb66a806955f5c168569c64b87077)
            check_type(argname="argument authorization_scopes", value=authorization_scopes, expected_type=typing.Tuple[type_hints["authorization_scopes"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast("CognitoAuthorizer", jsii.invoke(self, "withScopes", [*authorization_scopes]))

    @builtins.property
    @jsii.member(jsii_name="userPools")
    def user_pools(self) -> typing.List[_aws_cdk_aws_cognito_ceddda9d.IUserPool]:
        '''(experimental) The Cognito user pools associated with this authorizer.

        :stability: experimental
        '''
        return typing.cast(typing.List[_aws_cdk_aws_cognito_ceddda9d.IUserPool], jsii.get(self, "userPools"))


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.CognitoAuthorizerProps",
    jsii_struct_bases=[],
    name_mapping={
        "authorizer_id": "authorizerId",
        "user_pools": "userPools",
        "authorization_scopes": "authorizationScopes",
    },
)
class CognitoAuthorizerProps:
    def __init__(
        self,
        *,
        authorizer_id: builtins.str,
        user_pools: typing.Sequence[_aws_cdk_aws_cognito_ceddda9d.IUserPool],
        authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Properties used to configure a cognito authorizer.

        :param authorizer_id: (experimental) Unique identifier for this authorizer.
        :param user_pools: (experimental) The Cognito user pools associated with this authorizer.
        :param authorization_scopes: (experimental) A list of authorization scopes configured on the method. When used as the default authorizer, these scopes will be applied to all methods without an authorizer at the integration level. Default: []

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62ee5045c6a49973b02f825688c3321a300b9100cdd48a84a93dbe932ffac51a)
            check_type(argname="argument authorizer_id", value=authorizer_id, expected_type=type_hints["authorizer_id"])
            check_type(argname="argument user_pools", value=user_pools, expected_type=type_hints["user_pools"])
            check_type(argname="argument authorization_scopes", value=authorization_scopes, expected_type=type_hints["authorization_scopes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "authorizer_id": authorizer_id,
            "user_pools": user_pools,
        }
        if authorization_scopes is not None:
            self._values["authorization_scopes"] = authorization_scopes

    @builtins.property
    def authorizer_id(self) -> builtins.str:
        '''(experimental) Unique identifier for this authorizer.

        :stability: experimental
        '''
        result = self._values.get("authorizer_id")
        assert result is not None, "Required property 'authorizer_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_pools(self) -> typing.List[_aws_cdk_aws_cognito_ceddda9d.IUserPool]:
        '''(experimental) The Cognito user pools associated with this authorizer.

        :stability: experimental
        '''
        result = self._values.get("user_pools")
        assert result is not None, "Required property 'user_pools' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_cognito_ceddda9d.IUserPool], result)

    @builtins.property
    def authorization_scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of authorization scopes configured on the method.

        When used as the default authorizer, these scopes will be
        applied to all methods without an authorizer at the integration level.

        :default: []

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html#cfn-apigateway-method-authorizationscopes
        :stability: experimental
        '''
        result = self._values.get("authorization_scopes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoAuthorizerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CustomAuthorizer(
    Authorizer,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-prototyping-sdk/type-safe-api.CustomAuthorizer",
):
    '''(experimental) An authorizer that uses a lambda function to authorize requests.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        authorizer_id: builtins.str,
        function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        authorizer_result_ttl_in_seconds: typing.Optional[jsii.Number] = None,
        identity_source: typing.Optional[builtins.str] = None,
        type: typing.Optional["CustomAuthorizerType"] = None,
    ) -> None:
        '''
        :param authorizer_id: (experimental) Unique identifier for this authorizer.
        :param function: (experimental) The lambda function used to authorize requests.
        :param authorizer_result_ttl_in_seconds: (experimental) The number of seconds during which the authorizer result is cached. Default: 300
        :param identity_source: (experimental) The source of the identity in an incoming request. Default: "method.request.header.Authorization"
        :param type: (experimental) The type of custom authorizer. Default: CustomAuthorizerType.TOKEN

        :stability: experimental
        '''
        props = CustomAuthorizerProps(
            authorizer_id=authorizer_id,
            function=function,
            authorizer_result_ttl_in_seconds=authorizer_result_ttl_in_seconds,
            identity_source=identity_source,
            type=type,
        )

        jsii.create(self.__class__, self, [props])

    @builtins.property
    @jsii.member(jsii_name="authorizerResultTtlInSeconds")
    def authorizer_result_ttl_in_seconds(self) -> jsii.Number:
        '''(experimental) The number of seconds during which the authorizer result is cached.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "authorizerResultTtlInSeconds"))

    @builtins.property
    @jsii.member(jsii_name="function")
    def function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''(experimental) The lambda function used to authorize requests.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "function"))

    @builtins.property
    @jsii.member(jsii_name="identitySource")
    def identity_source(self) -> builtins.str:
        '''(experimental) The source of the identity in an incoming request.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html#cfn-apigateway-authorizer-identitysource
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "identitySource"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> "CustomAuthorizerType":
        '''(experimental) The type of custom authorizer.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html#cfn-apigateway-authorizer-type
        :stability: experimental
        '''
        return typing.cast("CustomAuthorizerType", jsii.get(self, "type"))


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.CustomAuthorizerProps",
    jsii_struct_bases=[],
    name_mapping={
        "authorizer_id": "authorizerId",
        "function": "function",
        "authorizer_result_ttl_in_seconds": "authorizerResultTtlInSeconds",
        "identity_source": "identitySource",
        "type": "type",
    },
)
class CustomAuthorizerProps:
    def __init__(
        self,
        *,
        authorizer_id: builtins.str,
        function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        authorizer_result_ttl_in_seconds: typing.Optional[jsii.Number] = None,
        identity_source: typing.Optional[builtins.str] = None,
        type: typing.Optional["CustomAuthorizerType"] = None,
    ) -> None:
        '''(experimental) Properties used to configure a custom authorizer.

        :param authorizer_id: (experimental) Unique identifier for this authorizer.
        :param function: (experimental) The lambda function used to authorize requests.
        :param authorizer_result_ttl_in_seconds: (experimental) The number of seconds during which the authorizer result is cached. Default: 300
        :param identity_source: (experimental) The source of the identity in an incoming request. Default: "method.request.header.Authorization"
        :param type: (experimental) The type of custom authorizer. Default: CustomAuthorizerType.TOKEN

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c71002e919737a01a6f2695f649dec4346581e930ea1d02961439b5ea0b0fe9)
            check_type(argname="argument authorizer_id", value=authorizer_id, expected_type=type_hints["authorizer_id"])
            check_type(argname="argument function", value=function, expected_type=type_hints["function"])
            check_type(argname="argument authorizer_result_ttl_in_seconds", value=authorizer_result_ttl_in_seconds, expected_type=type_hints["authorizer_result_ttl_in_seconds"])
            check_type(argname="argument identity_source", value=identity_source, expected_type=type_hints["identity_source"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "authorizer_id": authorizer_id,
            "function": function,
        }
        if authorizer_result_ttl_in_seconds is not None:
            self._values["authorizer_result_ttl_in_seconds"] = authorizer_result_ttl_in_seconds
        if identity_source is not None:
            self._values["identity_source"] = identity_source
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def authorizer_id(self) -> builtins.str:
        '''(experimental) Unique identifier for this authorizer.

        :stability: experimental
        '''
        result = self._values.get("authorizer_id")
        assert result is not None, "Required property 'authorizer_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''(experimental) The lambda function used to authorize requests.

        :stability: experimental
        '''
        result = self._values.get("function")
        assert result is not None, "Required property 'function' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, result)

    @builtins.property
    def authorizer_result_ttl_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of seconds during which the authorizer result is cached.

        :default: 300

        :stability: experimental
        '''
        result = self._values.get("authorizer_result_ttl_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def identity_source(self) -> typing.Optional[builtins.str]:
        '''(experimental) The source of the identity in an incoming request.

        :default: "method.request.header.Authorization"

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html#cfn-apigateway-authorizer-identitysource
        :stability: experimental
        '''
        result = self._values.get("identity_source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional["CustomAuthorizerType"]:
        '''(experimental) The type of custom authorizer.

        :default: CustomAuthorizerType.TOKEN

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html#cfn-apigateway-authorizer-type
        :stability: experimental
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional["CustomAuthorizerType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomAuthorizerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-prototyping-sdk/type-safe-api.CustomAuthorizerType")
class CustomAuthorizerType(enum.Enum):
    '''(experimental) The type of custom authorizer.

    :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html#cfn-apigateway-authorizer-type
    :stability: experimental
    '''

    TOKEN = "TOKEN"
    '''(experimental) A custom authorizer that uses a Lambda function.

    :stability: experimental
    '''
    REQUEST = "REQUEST"
    '''(experimental) An authorizer that uses a Lambda function using incoming request parameters.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.DocumentationConfiguration",
    jsii_struct_bases=[],
    name_mapping={"formats": "formats"},
)
class DocumentationConfiguration:
    def __init__(self, *, formats: typing.Sequence["DocumentationFormat"]) -> None:
        '''(experimental) Configuration for generated documentation.

        :param formats: (experimental) Formats for generated documentation.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0fd7650b3ad306974000ccd92a709cb54595a5ac502052bb19f206b5ad36d3e)
            check_type(argname="argument formats", value=formats, expected_type=type_hints["formats"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "formats": formats,
        }

    @builtins.property
    def formats(self) -> typing.List["DocumentationFormat"]:
        '''(experimental) Formats for generated documentation.

        :stability: experimental
        '''
        result = self._values.get("formats")
        assert result is not None, "Required property 'formats' is missing"
        return typing.cast(typing.List["DocumentationFormat"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DocumentationConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-prototyping-sdk/type-safe-api.DocumentationFormat")
class DocumentationFormat(enum.Enum):
    '''(experimental) Formats for documentation generation.

    :stability: experimental
    '''

    HTML_REDOC = "HTML_REDOC"
    '''(experimental) HTML Documentation generated by redoc.

    :see: https://github.com/Redocly/redoc
    :stability: experimental
    '''
    HTML2 = "HTML2"
    '''(experimental) OpenAPI Generator 'html2' documentation.

    :see: https://github.com/OpenAPITools/openapi-generator/blob/master/docs/generators/html2.md
    :stability: experimental
    '''
    MARKDOWN = "MARKDOWN"
    '''(experimental) OpenAPI Generator 'markdown' documentation.

    :see: https://github.com/OpenAPITools/openapi-generator/blob/master/docs/generators/markdown.md
    :stability: experimental
    '''
    PLANTUML = "PLANTUML"
    '''(experimental) OpenAPI Generator 'plantuml' documentation.

    :see: https://github.com/OpenAPITools/openapi-generator/blob/master/docs/generators/plantuml.md
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.GeneratedCodeOptions",
    jsii_struct_bases=[],
    name_mapping={"java": "java", "python": "python", "typescript": "typescript"},
)
class GeneratedCodeOptions:
    def __init__(
        self,
        *,
        java: typing.Optional[typing.Union[_projen_java_04054675.JavaProjectOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        python: typing.Optional[typing.Union[_projen_python_04054675.PythonProjectOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        typescript: typing.Optional[typing.Union[_projen_typescript_04054675.TypeScriptProjectOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Options for generated clients.

        :param java: (experimental) Options for a generated java project. These override the default inferred options.
        :param python: (experimental) Options for a generated python project. These override the default inferred options.
        :param typescript: (experimental) Options for a generated typescript project. These override the default inferred options.

        :stability: experimental
        '''
        if isinstance(java, dict):
            java = _projen_java_04054675.JavaProjectOptions(**java)
        if isinstance(python, dict):
            python = _projen_python_04054675.PythonProjectOptions(**python)
        if isinstance(typescript, dict):
            typescript = _projen_typescript_04054675.TypeScriptProjectOptions(**typescript)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23f41be8cb8518404a72409561f18dfc9dcf036ff46fc15a66438b4aad08e69c)
            check_type(argname="argument java", value=java, expected_type=type_hints["java"])
            check_type(argname="argument python", value=python, expected_type=type_hints["python"])
            check_type(argname="argument typescript", value=typescript, expected_type=type_hints["typescript"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if java is not None:
            self._values["java"] = java
        if python is not None:
            self._values["python"] = python
        if typescript is not None:
            self._values["typescript"] = typescript

    @builtins.property
    def java(self) -> typing.Optional[_projen_java_04054675.JavaProjectOptions]:
        '''(experimental) Options for a generated java project.

        These override the default inferred options.

        :stability: experimental
        '''
        result = self._values.get("java")
        return typing.cast(typing.Optional[_projen_java_04054675.JavaProjectOptions], result)

    @builtins.property
    def python(self) -> typing.Optional[_projen_python_04054675.PythonProjectOptions]:
        '''(experimental) Options for a generated python project.

        These override the default inferred options.

        :stability: experimental
        '''
        result = self._values.get("python")
        return typing.cast(typing.Optional[_projen_python_04054675.PythonProjectOptions], result)

    @builtins.property
    def typescript(
        self,
    ) -> typing.Optional[_projen_typescript_04054675.TypeScriptProjectOptions]:
        '''(experimental) Options for a generated typescript project.

        These override the default inferred options.

        :stability: experimental
        '''
        result = self._values.get("typescript")
        return typing.cast(typing.Optional[_projen_typescript_04054675.TypeScriptProjectOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GeneratedCodeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.GeneratedCodeProjects",
    jsii_struct_bases=[],
    name_mapping={"java": "java", "python": "python", "typescript": "typescript"},
)
class GeneratedCodeProjects:
    def __init__(
        self,
        *,
        java: typing.Optional[_projen_java_04054675.JavaProject] = None,
        python: typing.Optional[_projen_python_04054675.PythonProject] = None,
        typescript: typing.Optional[_projen_typescript_04054675.TypeScriptProject] = None,
    ) -> None:
        '''(experimental) Generated code projects.

        :param java: (experimental) Generated java project.
        :param python: (experimental) Generated python project.
        :param typescript: (experimental) Generated typescript project.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0f400533db43e5c38defa1fec15b1bd673fa5a195759697379ba33d179a60b5)
            check_type(argname="argument java", value=java, expected_type=type_hints["java"])
            check_type(argname="argument python", value=python, expected_type=type_hints["python"])
            check_type(argname="argument typescript", value=typescript, expected_type=type_hints["typescript"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if java is not None:
            self._values["java"] = java
        if python is not None:
            self._values["python"] = python
        if typescript is not None:
            self._values["typescript"] = typescript

    @builtins.property
    def java(self) -> typing.Optional[_projen_java_04054675.JavaProject]:
        '''(experimental) Generated java project.

        :stability: experimental
        '''
        result = self._values.get("java")
        return typing.cast(typing.Optional[_projen_java_04054675.JavaProject], result)

    @builtins.property
    def python(self) -> typing.Optional[_projen_python_04054675.PythonProject]:
        '''(experimental) Generated python project.

        :stability: experimental
        '''
        result = self._values.get("python")
        return typing.cast(typing.Optional[_projen_python_04054675.PythonProject], result)

    @builtins.property
    def typescript(
        self,
    ) -> typing.Optional[_projen_typescript_04054675.TypeScriptProject]:
        '''(experimental) Generated typescript project.

        :stability: experimental
        '''
        result = self._values.get("typescript")
        return typing.cast(typing.Optional[_projen_typescript_04054675.TypeScriptProject], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GeneratedCodeProjects(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.GeneratedLibraryOptions",
    jsii_struct_bases=[],
    name_mapping={"typescript_react_query_hooks": "typescriptReactQueryHooks"},
)
class GeneratedLibraryOptions:
    def __init__(
        self,
        *,
        typescript_react_query_hooks: typing.Optional[typing.Union[_projen_typescript_04054675.TypeScriptProjectOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Options for generated libraries.

        :param typescript_react_query_hooks: (experimental) Options for the generated typescript react-query hooks library. These override the default inferred options.

        :stability: experimental
        '''
        if isinstance(typescript_react_query_hooks, dict):
            typescript_react_query_hooks = _projen_typescript_04054675.TypeScriptProjectOptions(**typescript_react_query_hooks)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aaba6490bdd657ac25f54e9f2eaacb24cb65c191d4ec347ee3547a98abae3956)
            check_type(argname="argument typescript_react_query_hooks", value=typescript_react_query_hooks, expected_type=type_hints["typescript_react_query_hooks"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if typescript_react_query_hooks is not None:
            self._values["typescript_react_query_hooks"] = typescript_react_query_hooks

    @builtins.property
    def typescript_react_query_hooks(
        self,
    ) -> typing.Optional[_projen_typescript_04054675.TypeScriptProjectOptions]:
        '''(experimental) Options for the generated typescript react-query hooks library.

        These override the default inferred options.

        :stability: experimental
        '''
        result = self._values.get("typescript_react_query_hooks")
        return typing.cast(typing.Optional[_projen_typescript_04054675.TypeScriptProjectOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GeneratedLibraryOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.GeneratedLibraryProjects",
    jsii_struct_bases=[],
    name_mapping={"typescript_react_query_hooks": "typescriptReactQueryHooks"},
)
class GeneratedLibraryProjects:
    def __init__(
        self,
        *,
        typescript_react_query_hooks: typing.Optional[_projen_typescript_04054675.TypeScriptProject] = None,
    ) -> None:
        '''(experimental) Generated library projects.

        :param typescript_react_query_hooks: (experimental) Generated typescript react-query hooks project.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31ee7e756a53a88db35aef6ee5d346bfd3c90aab725573d11722d24b6973ea0e)
            check_type(argname="argument typescript_react_query_hooks", value=typescript_react_query_hooks, expected_type=type_hints["typescript_react_query_hooks"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if typescript_react_query_hooks is not None:
            self._values["typescript_react_query_hooks"] = typescript_react_query_hooks

    @builtins.property
    def typescript_react_query_hooks(
        self,
    ) -> typing.Optional[_projen_typescript_04054675.TypeScriptProject]:
        '''(experimental) Generated typescript react-query hooks project.

        :stability: experimental
        '''
        result = self._values.get("typescript_react_query_hooks")
        return typing.cast(typing.Optional[_projen_typescript_04054675.TypeScriptProject], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GeneratedLibraryProjects(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IamAuthorizer(
    Authorizer,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-prototyping-sdk/type-safe-api.IamAuthorizer",
):
    '''(experimental) An IAM authorizer.

    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.InfrastructureConfiguration",
    jsii_struct_bases=[],
    name_mapping={"language": "language", "options": "options"},
)
class InfrastructureConfiguration:
    def __init__(
        self,
        *,
        language: "Language",
        options: typing.Optional[typing.Union[GeneratedCodeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Configuration for generated infrastructure.

        :param language: (experimental) The language to generate the type-safe CDK infrastructure in.
        :param options: (experimental) Options for the infrastructure package. Note that only those provided for the specified language will apply.

        :stability: experimental
        '''
        if isinstance(options, dict):
            options = GeneratedCodeOptions(**options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42832742ccb56b4504cad0e669390b735f9f726fc938f2b7eb2d7878b53e3faf)
            check_type(argname="argument language", value=language, expected_type=type_hints["language"])
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "language": language,
        }
        if options is not None:
            self._values["options"] = options

    @builtins.property
    def language(self) -> "Language":
        '''(experimental) The language to generate the type-safe CDK infrastructure in.

        :stability: experimental
        '''
        result = self._values.get("language")
        assert result is not None, "Required property 'language' is missing"
        return typing.cast("Language", result)

    @builtins.property
    def options(self) -> typing.Optional[GeneratedCodeOptions]:
        '''(experimental) Options for the infrastructure package.

        Note that only those provided for the specified language will apply.

        :stability: experimental
        '''
        result = self._values.get("options")
        return typing.cast(typing.Optional[GeneratedCodeOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InfrastructureConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Integration(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-prototyping-sdk/type-safe-api.Integration",
):
    '''(experimental) An integration for an API operation.

    You can extend this to implement your own integration if you like.

    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        *,
        api: _aws_cdk_aws_apigateway_ceddda9d.SpecRestApi,
        operation_id: builtins.str,
        scope: _constructs_77d1e7e8.Construct,
        method: builtins.str,
        path: builtins.str,
    ) -> None:
        '''(experimental) Grant permissions for the API to invoke the integration.

        :param api: (experimental) The api to grant permissions for.
        :param operation_id: (experimental) The ID of the operation for which permissions are being granted.
        :param scope: (experimental) The scope in which permission resources can be created.
        :param method: (experimental) The http method of this operation.
        :param path: (experimental) The path of this operation in the api.

        :stability: experimental
        '''
        _props = IntegrationGrantProps(
            api=api, operation_id=operation_id, scope=scope, method=method, path=path
        )

        return typing.cast(None, jsii.invoke(self, "grant", [_props]))

    @jsii.member(jsii_name="render")
    @abc.abstractmethod
    def render(
        self,
        *,
        operation_id: builtins.str,
        scope: _constructs_77d1e7e8.Construct,
        method: builtins.str,
        path: builtins.str,
    ) -> ApiGatewayIntegration:
        '''(experimental) Render the integration into an API Gateway OpenAPI extension.

        :param operation_id: (experimental) The ID of the operation being rendered.
        :param scope: (experimental) The scope in which the integration is being rendered.
        :param method: (experimental) The http method of this operation.
        :param path: (experimental) The path of this operation in the api.

        :stability: experimental
        '''
        ...


class _IntegrationProxy(Integration):
    @jsii.member(jsii_name="render")
    def render(
        self,
        *,
        operation_id: builtins.str,
        scope: _constructs_77d1e7e8.Construct,
        method: builtins.str,
        path: builtins.str,
    ) -> ApiGatewayIntegration:
        '''(experimental) Render the integration into an API Gateway OpenAPI extension.

        :param operation_id: (experimental) The ID of the operation being rendered.
        :param scope: (experimental) The scope in which the integration is being rendered.
        :param method: (experimental) The http method of this operation.
        :param path: (experimental) The path of this operation in the api.

        :stability: experimental
        '''
        props = IntegrationRenderProps(
            operation_id=operation_id, scope=scope, method=method, path=path
        )

        return typing.cast(ApiGatewayIntegration, jsii.invoke(self, "render", [props]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, Integration).__jsii_proxy_class__ = lambda : _IntegrationProxy


class Integrations(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-prototyping-sdk/type-safe-api.Integrations",
):
    '''(experimental) A collection of integrations to connect API operations with a backend to service requests.

    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="lambda")
    @builtins.classmethod
    def lambda_(
        cls,
        lambda_function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    ) -> "LambdaIntegration":
        '''(experimental) An integration that invokes a lambda function to service the request.

        :param lambda_function: the function to invoke.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e282d4562d6f4a6d2012128cec34ed04419998a73c33d70b6d7ac593f6da8f5)
            check_type(argname="argument lambda_function", value=lambda_function, expected_type=type_hints["lambda_function"])
        return typing.cast("LambdaIntegration", jsii.sinvoke(cls, "lambda", [lambda_function]))


class LambdaIntegration(
    Integration,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-prototyping-sdk/type-safe-api.LambdaIntegration",
):
    '''(experimental) A lambda integration.

    :stability: experimental
    '''

    def __init__(self, lambda_function: _aws_cdk_aws_lambda_ceddda9d.IFunction) -> None:
        '''
        :param lambda_function: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4f33cbf9ca3cf26ca56b9477805b0ee2228ee2f97e63a0addace46ae5267b4d)
            check_type(argname="argument lambda_function", value=lambda_function, expected_type=type_hints["lambda_function"])
        jsii.create(self.__class__, self, [lambda_function])

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        *,
        api: _aws_cdk_aws_apigateway_ceddda9d.SpecRestApi,
        operation_id: builtins.str,
        scope: _constructs_77d1e7e8.Construct,
        method: builtins.str,
        path: builtins.str,
    ) -> None:
        '''(experimental) Grant API Gateway permissions to invoke the lambda.

        :param api: (experimental) The api to grant permissions for.
        :param operation_id: (experimental) The ID of the operation for which permissions are being granted.
        :param scope: (experimental) The scope in which permission resources can be created.
        :param method: (experimental) The http method of this operation.
        :param path: (experimental) The path of this operation in the api.

        :stability: experimental
        '''
        __0 = IntegrationGrantProps(
            api=api, operation_id=operation_id, scope=scope, method=method, path=path
        )

        return typing.cast(None, jsii.invoke(self, "grant", [__0]))

    @jsii.member(jsii_name="render")
    def render(
        self,
        *,
        operation_id: builtins.str,
        scope: _constructs_77d1e7e8.Construct,
        method: builtins.str,
        path: builtins.str,
    ) -> ApiGatewayIntegration:
        '''(experimental) Render the lambda integration as a snippet of OpenAPI.

        :param operation_id: (experimental) The ID of the operation being rendered.
        :param scope: (experimental) The scope in which the integration is being rendered.
        :param method: (experimental) The http method of this operation.
        :param path: (experimental) The path of this operation in the api.

        :stability: experimental
        '''
        props = IntegrationRenderProps(
            operation_id=operation_id, scope=scope, method=method, path=path
        )

        return typing.cast(ApiGatewayIntegration, jsii.invoke(self, "render", [props]))


@jsii.enum(jsii_type="@aws-prototyping-sdk/type-safe-api.Language")
class Language(enum.Enum):
    '''(experimental) Supported languages for runtimes and infrastructure.

    :stability: experimental
    '''

    TYPESCRIPT = "TYPESCRIPT"
    '''
    :stability: experimental
    '''
    PYTHON = "PYTHON"
    '''
    :stability: experimental
    '''
    JAVA = "JAVA"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="@aws-prototyping-sdk/type-safe-api.Library")
class Library(enum.Enum):
    '''(experimental) Supported libraries for code generation.

    :stability: experimental
    '''

    TYPESCRIPT_REACT_QUERY_HOOKS = "TYPESCRIPT_REACT_QUERY_HOOKS"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.LibraryConfiguration",
    jsii_struct_bases=[],
    name_mapping={"libraries": "libraries", "options": "options"},
)
class LibraryConfiguration:
    def __init__(
        self,
        *,
        libraries: typing.Sequence[Library],
        options: typing.Optional[typing.Union[GeneratedLibraryOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Configuration for generated libraries.

        :param libraries: (experimental) The library to generate.
        :param options: (experimental) Options for the generated library package. Note that only options for the specified libraries will apply

        :stability: experimental
        '''
        if isinstance(options, dict):
            options = GeneratedLibraryOptions(**options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf885e298875e06aa5677eb9355657441701a5f252c8eca8317f989a12fb7d82)
            check_type(argname="argument libraries", value=libraries, expected_type=type_hints["libraries"])
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "libraries": libraries,
        }
        if options is not None:
            self._values["options"] = options

    @builtins.property
    def libraries(self) -> typing.List[Library]:
        '''(experimental) The library to generate.

        :stability: experimental
        '''
        result = self._values.get("libraries")
        assert result is not None, "Required property 'libraries' is missing"
        return typing.cast(typing.List[Library], result)

    @builtins.property
    def options(self) -> typing.Optional[GeneratedLibraryOptions]:
        '''(experimental) Options for the generated library package.

        Note that only options for the specified libraries will apply

        :stability: experimental
        '''
        result = self._values.get("options")
        return typing.cast(typing.Optional[GeneratedLibraryOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LibraryConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.ManagedRule",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "vendor": "vendor"},
)
class ManagedRule:
    def __init__(self, *, name: builtins.str, vendor: builtins.str) -> None:
        '''
        :param name: (experimental) The name of the managed rule group. You use this, along with the vendor name, to identify the rule group.
        :param vendor: (experimental) The name of the managed rule group vendor. You use this, along with the rule group name, to identify the rule group.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5526168b6baf723196f879ba4ca6bcce6f57e83cf0e96d3c912a0ab422a07e3)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument vendor", value=vendor, expected_type=type_hints["vendor"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "vendor": vendor,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The name of the managed rule group.

        You use this, along with the vendor name, to identify the rule group.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vendor(self) -> builtins.str:
        '''(experimental) The name of the managed rule group vendor.

        You use this, along with the rule group name, to identify the rule group.

        :stability: experimental
        '''
        result = self._values.get("vendor")
        assert result is not None, "Required property 'vendor' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.MethodAndPath",
    jsii_struct_bases=[],
    name_mapping={"method": "method", "path": "path"},
)
class MethodAndPath:
    def __init__(self, *, method: builtins.str, path: builtins.str) -> None:
        '''(experimental) Structure to contain an API operation's method and path.

        :param method: (experimental) The http method of this operation.
        :param path: (experimental) The path of this operation in the api.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__002fb094dfb3c5bb8ab5a5455ef75fa49e10214af4f996e8ec7c98bfb10fe67a)
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "method": method,
            "path": path,
        }

    @builtins.property
    def method(self) -> builtins.str:
        '''(experimental) The http method of this operation.

        :stability: experimental
        '''
        result = self._values.get("method")
        assert result is not None, "Required property 'method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path(self) -> builtins.str:
        '''(experimental) The path of this operation in the api.

        :stability: experimental
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MethodAndPath(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.ModelConfiguration",
    jsii_struct_bases=[],
    name_mapping={"language": "language", "options": "options"},
)
class ModelConfiguration:
    def __init__(
        self,
        *,
        language: "ModelLanguage",
        options: typing.Union["ModelOptions", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''(experimental) Configuration for modelling the API.

        :param language: (experimental) The language the API model is defined in.
        :param options: (experimental) Options for the API model.

        :stability: experimental
        '''
        if isinstance(options, dict):
            options = ModelOptions(**options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86eb139bc129f96c7fb27199a03837046b0d025d1e87b5911e8cf218d7f4eae6)
            check_type(argname="argument language", value=language, expected_type=type_hints["language"])
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "language": language,
            "options": options,
        }

    @builtins.property
    def language(self) -> "ModelLanguage":
        '''(experimental) The language the API model is defined in.

        :stability: experimental
        '''
        result = self._values.get("language")
        assert result is not None, "Required property 'language' is missing"
        return typing.cast("ModelLanguage", result)

    @builtins.property
    def options(self) -> "ModelOptions":
        '''(experimental) Options for the API model.

        :stability: experimental
        '''
        result = self._values.get("options")
        assert result is not None, "Required property 'options' is missing"
        return typing.cast("ModelOptions", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-prototyping-sdk/type-safe-api.ModelLanguage")
class ModelLanguage(enum.Enum):
    '''(experimental) The model definition language.

    :stability: experimental
    '''

    SMITHY = "SMITHY"
    '''(experimental) Smithy.

    :see: https://smithy.io/2.0/
    :stability: experimental
    '''
    OPENAPI = "OPENAPI"
    '''(experimental) OpenAPI.

    :see: https://www.openapis.org/
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.ModelOptions",
    jsii_struct_bases=[],
    name_mapping={"openapi": "openapi", "smithy": "smithy"},
)
class ModelOptions:
    def __init__(
        self,
        *,
        openapi: typing.Optional[typing.Union["OpenApiModelOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        smithy: typing.Optional[typing.Union["SmithyModelOptions", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Options for models.

        :param openapi: (experimental) Options for the OpenAPI model - required when model language is OPENAPI.
        :param smithy: (experimental) Options for the Smithy model - required when model language is SMITHY.

        :stability: experimental
        '''
        if isinstance(openapi, dict):
            openapi = OpenApiModelOptions(**openapi)
        if isinstance(smithy, dict):
            smithy = SmithyModelOptions(**smithy)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19b2eb4034a9eda1968994c2e7da74dca6c331bf42f0c1dc88c09da184b11ef4)
            check_type(argname="argument openapi", value=openapi, expected_type=type_hints["openapi"])
            check_type(argname="argument smithy", value=smithy, expected_type=type_hints["smithy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if openapi is not None:
            self._values["openapi"] = openapi
        if smithy is not None:
            self._values["smithy"] = smithy

    @builtins.property
    def openapi(self) -> typing.Optional["OpenApiModelOptions"]:
        '''(experimental) Options for the OpenAPI model - required when model language is OPENAPI.

        :stability: experimental
        '''
        result = self._values.get("openapi")
        return typing.cast(typing.Optional["OpenApiModelOptions"], result)

    @builtins.property
    def smithy(self) -> typing.Optional["SmithyModelOptions"]:
        '''(experimental) Options for the Smithy model - required when model language is SMITHY.

        :stability: experimental
        '''
        result = self._values.get("smithy")
        return typing.cast(typing.Optional["SmithyModelOptions"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NoneAuthorizer(
    Authorizer,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-prototyping-sdk/type-safe-api.NoneAuthorizer",
):
    '''(experimental) No authorizer.

    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])


class OpenApiDefinition(
    _projen_04054675.Component,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-prototyping-sdk/type-safe-api.OpenApiDefinition",
):
    '''(experimental) The OpenAPI Spec.

    :stability: experimental
    '''

    def __init__(
        self,
        project: "TypeSafeApiModelProject",
        *,
        open_api_options: typing.Union["OpenApiModelOptions", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param project: -
        :param open_api_options: (experimental) Options for the openapi model.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__370ebffac0840359674dee761aaeaa906d40299ef3ec2d6323f2214155e1db2d)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        options = OpenApiDefinitionOptions(open_api_options=open_api_options)

        jsii.create(self.__class__, self, [project, options])

    @builtins.property
    @jsii.member(jsii_name="openApiSpecificationPath")
    def open_api_specification_path(self) -> builtins.str:
        '''(experimental) Path to the root OpenAPI specification file.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "openApiSpecificationPath"))


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.OpenApiDefinitionOptions",
    jsii_struct_bases=[],
    name_mapping={"open_api_options": "openApiOptions"},
)
class OpenApiDefinitionOptions:
    def __init__(
        self,
        *,
        open_api_options: typing.Union["OpenApiModelOptions", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''(experimental) Options for the OpenAPI Spec.

        :param open_api_options: (experimental) Options for the openapi model.

        :stability: experimental
        '''
        if isinstance(open_api_options, dict):
            open_api_options = OpenApiModelOptions(**open_api_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__591f8c9caef1c0f0144c3c8f46e6c9515a9b59283a269f9a55ff68f0655c28bd)
            check_type(argname="argument open_api_options", value=open_api_options, expected_type=type_hints["open_api_options"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "open_api_options": open_api_options,
        }

    @builtins.property
    def open_api_options(self) -> "OpenApiModelOptions":
        '''(experimental) Options for the openapi model.

        :stability: experimental
        '''
        result = self._values.get("open_api_options")
        assert result is not None, "Required property 'open_api_options' is missing"
        return typing.cast("OpenApiModelOptions", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpenApiDefinitionOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.OpenApiModelOptions",
    jsii_struct_bases=[],
    name_mapping={"title": "title"},
)
class OpenApiModelOptions:
    def __init__(self, *, title: builtins.str) -> None:
        '''(experimental) Options for the OpenAPI model.

        :param title: (experimental) The title in the OpenAPI specification.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4384c14a609de971de6d097c833aea11812d657157670113cb85f7eeca095985)
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "title": title,
        }

    @builtins.property
    def title(self) -> builtins.str:
        '''(experimental) The title in the OpenAPI specification.

        :stability: experimental
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpenApiModelOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.RuntimeConfiguration",
    jsii_struct_bases=[],
    name_mapping={"languages": "languages", "options": "options"},
)
class RuntimeConfiguration:
    def __init__(
        self,
        *,
        languages: typing.Sequence[Language],
        options: typing.Optional[typing.Union[GeneratedCodeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Configuration for generated runtime projects.

        :param languages: (experimental) The languages that runtime projects will be generated in. These projects can be used to provide type safety for both client and server projects.
        :param options: (experimental) Options for the generated runtimes. Note that only options provided for the specified languages will apply.

        :stability: experimental
        '''
        if isinstance(options, dict):
            options = GeneratedCodeOptions(**options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3be12f3081726e44a0f5ea07c36e418c48204b3fee82192c24e1eb2cb72d1f10)
            check_type(argname="argument languages", value=languages, expected_type=type_hints["languages"])
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "languages": languages,
        }
        if options is not None:
            self._values["options"] = options

    @builtins.property
    def languages(self) -> typing.List[Language]:
        '''(experimental) The languages that runtime projects will be generated in.

        These projects can be used to provide type safety for
        both client and server projects.

        :stability: experimental
        '''
        result = self._values.get("languages")
        assert result is not None, "Required property 'languages' is missing"
        return typing.cast(typing.List[Language], result)

    @builtins.property
    def options(self) -> typing.Optional[GeneratedCodeOptions]:
        '''(experimental) Options for the generated runtimes.

        Note that only options provided for the specified languages will apply.

        :stability: experimental
        '''
        result = self._values.get("options")
        return typing.cast(typing.Optional[GeneratedCodeOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RuntimeConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.SmithyCommon",
    jsii_struct_bases=[],
    name_mapping={"imports": "imports", "plugins": "plugins"},
)
class SmithyCommon:
    def __init__(
        self,
        *,
        imports: typing.Optional[typing.Sequence[builtins.str]] = None,
        plugins: typing.Optional[typing.Mapping[builtins.str, typing.Mapping[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Properties common to smithy plugins and the root smithy build.

        :param imports: (experimental) List of imports.
        :param plugins: (experimental) Plugins keyed by plugin id.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eef1a858c59c498786d12a5a49debb2c3a22b53c0435a8b44fac4d42f40f4c70)
            check_type(argname="argument imports", value=imports, expected_type=type_hints["imports"])
            check_type(argname="argument plugins", value=plugins, expected_type=type_hints["plugins"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if imports is not None:
            self._values["imports"] = imports
        if plugins is not None:
            self._values["plugins"] = plugins

    @builtins.property
    def imports(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of imports.

        :stability: experimental
        '''
        result = self._values.get("imports")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def plugins(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Mapping[builtins.str, typing.Any]]]:
        '''(experimental) Plugins keyed by plugin id.

        :stability: experimental
        '''
        result = self._values.get("plugins")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Mapping[builtins.str, typing.Any]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SmithyCommon(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SmithyDefinition(
    _projen_04054675.Component,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-prototyping-sdk/type-safe-api.SmithyDefinition",
):
    '''(experimental) Creates a project which transforms a Smithy model to OpenAPI.

    :stability: experimental
    '''

    def __init__(
        self,
        project: "TypeSafeApiModelProject",
        *,
        smithy_options: typing.Union["SmithyModelOptions", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param project: -
        :param smithy_options: (experimental) Smithy engine options.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da45c4bac118e04412e8a56eb9f701f415202aec168d3c649824a65a789cbdbd)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        options = SmithyDefinitionOptions(smithy_options=smithy_options)

        jsii.create(self.__class__, self, [project, options])

    @jsii.member(jsii_name="addDeps")
    def add_deps(self, *deps: builtins.str) -> None:
        '''(experimental) Add maven-style or local file dependencies to the smithy model project.

        :param deps: dependencies to add, eg "software.amazon.smithy:smithy-validation-model:1.27.2" or "file://../some/path/build/lib/my-shapes.jar.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__671cc8c9571996d8a6bd6cffe56aa2f3c23025d1e0f1b630b4a312786ae8d84a)
            check_type(argname="argument deps", value=deps, expected_type=typing.Tuple[type_hints["deps"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(None, jsii.invoke(self, "addDeps", [*deps]))

    @jsii.member(jsii_name="addSmithyDeps")
    def add_smithy_deps(self, *deps: "SmithyDefinition") -> None:
        '''(experimental) Add dependencies on other smithy models, such that their shapes can be imported in this project.

        :param deps: smithy definitions to depend on.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b4739ed02d1dd3269fca1e6cf1c9dda195085fbcf4af8a48df5573dbe28ee82)
            check_type(argname="argument deps", value=deps, expected_type=typing.Tuple[type_hints["deps"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(None, jsii.invoke(self, "addSmithyDeps", [*deps]))

    @builtins.property
    @jsii.member(jsii_name="gradleProjectName")
    def gradle_project_name(self) -> builtins.str:
        '''(experimental) Name of the gradle project.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "gradleProjectName"))

    @builtins.property
    @jsii.member(jsii_name="openApiSpecificationPath")
    def open_api_specification_path(self) -> builtins.str:
        '''(experimental) Path to the generated OpenAPI specification, relative to the project outdir.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "openApiSpecificationPath"))


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.SmithyDefinitionOptions",
    jsii_struct_bases=[],
    name_mapping={"smithy_options": "smithyOptions"},
)
class SmithyDefinitionOptions:
    def __init__(
        self,
        *,
        smithy_options: typing.Union["SmithyModelOptions", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''(experimental) Options for a smithy build project.

        :param smithy_options: (experimental) Smithy engine options.

        :stability: experimental
        '''
        if isinstance(smithy_options, dict):
            smithy_options = SmithyModelOptions(**smithy_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__036ba6d3e9b28066c60f4c0d3d8829c325d7b35770e1fe8c5d663bd4c2a2ce63)
            check_type(argname="argument smithy_options", value=smithy_options, expected_type=type_hints["smithy_options"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "smithy_options": smithy_options,
        }

    @builtins.property
    def smithy_options(self) -> "SmithyModelOptions":
        '''(experimental) Smithy engine options.

        :stability: experimental
        '''
        result = self._values.get("smithy_options")
        assert result is not None, "Required property 'smithy_options' is missing"
        return typing.cast("SmithyModelOptions", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SmithyDefinitionOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.SmithyMavenConfiguration",
    jsii_struct_bases=[],
    name_mapping={"dependencies": "dependencies", "repository_urls": "repositoryUrls"},
)
class SmithyMavenConfiguration:
    def __init__(
        self,
        *,
        dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        repository_urls: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Configuration for smithy maven dependencies.

        :param dependencies: (experimental) The dependencies used in the build.gradle and smithy-build.json files eg. software.amazon.smithy:smithy-validation-model:1.27.2 The following required dependencies are always added: - software.amazon.smithy:smithy-cli:1.27.2 - software.amazon.smithy:smithy-model:1.27.2 - software.amazon.smithy:smithy-openapi:1.27.2 - software.amazon.smithy:smithy-aws-traits:1.27.2 You can however override the version of these dependencies if required.
        :param repository_urls: (experimental) The repository urls used in the build.gradle and smithy-build.json files. Default: maven central and maven local

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0658a2f7e63bc2e040803cf6247a71762da6c3f26d27fc3438d10efa0c2b0014)
            check_type(argname="argument dependencies", value=dependencies, expected_type=type_hints["dependencies"])
            check_type(argname="argument repository_urls", value=repository_urls, expected_type=type_hints["repository_urls"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dependencies is not None:
            self._values["dependencies"] = dependencies
        if repository_urls is not None:
            self._values["repository_urls"] = repository_urls

    @builtins.property
    def dependencies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The dependencies used in the build.gradle and smithy-build.json files eg. software.amazon.smithy:smithy-validation-model:1.27.2 The following required dependencies are always added: - software.amazon.smithy:smithy-cli:1.27.2 - software.amazon.smithy:smithy-model:1.27.2 - software.amazon.smithy:smithy-openapi:1.27.2 - software.amazon.smithy:smithy-aws-traits:1.27.2 You can however override the version of these dependencies if required.

        :stability: experimental
        '''
        result = self._values.get("dependencies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def repository_urls(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The repository urls used in the build.gradle and smithy-build.json files.

        :default: maven central and maven local

        :stability: experimental
        '''
        result = self._values.get("repository_urls")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SmithyMavenConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.SmithyModelOptions",
    jsii_struct_bases=[],
    name_mapping={
        "service_name": "serviceName",
        "ignore_gradle_wrapper": "ignoreGradleWrapper",
        "ignore_smithy_build_output": "ignoreSmithyBuildOutput",
        "smithy_build_options": "smithyBuildOptions",
    },
)
class SmithyModelOptions:
    def __init__(
        self,
        *,
        service_name: typing.Union["SmithyServiceName", typing.Dict[builtins.str, typing.Any]],
        ignore_gradle_wrapper: typing.Optional[builtins.bool] = None,
        ignore_smithy_build_output: typing.Optional[builtins.bool] = None,
        smithy_build_options: typing.Optional[typing.Union["SmithyBuildOptions", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Options for a Smithy model.

        :param service_name: (experimental) Smithy service name.
        :param ignore_gradle_wrapper: (experimental) Set to false if you would like to check in your gradle wrapper. Do so if you would like to use a different version of gradle to the one provided by default Default: true
        :param ignore_smithy_build_output: (experimental) Set to false if you would like to check in your smithy build output or have more fine-grained control over what is checked in, eg if you add other projections to the smithy-build.json file. Default: true
        :param smithy_build_options: (experimental) Smithy build options.

        :stability: experimental
        '''
        if isinstance(service_name, dict):
            service_name = SmithyServiceName(**service_name)
        if isinstance(smithy_build_options, dict):
            smithy_build_options = SmithyBuildOptions(**smithy_build_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1182563a4207fde8baf185b6ac26b24239cff2142fe1cf342b86e5c28d28f024)
            check_type(argname="argument service_name", value=service_name, expected_type=type_hints["service_name"])
            check_type(argname="argument ignore_gradle_wrapper", value=ignore_gradle_wrapper, expected_type=type_hints["ignore_gradle_wrapper"])
            check_type(argname="argument ignore_smithy_build_output", value=ignore_smithy_build_output, expected_type=type_hints["ignore_smithy_build_output"])
            check_type(argname="argument smithy_build_options", value=smithy_build_options, expected_type=type_hints["smithy_build_options"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "service_name": service_name,
        }
        if ignore_gradle_wrapper is not None:
            self._values["ignore_gradle_wrapper"] = ignore_gradle_wrapper
        if ignore_smithy_build_output is not None:
            self._values["ignore_smithy_build_output"] = ignore_smithy_build_output
        if smithy_build_options is not None:
            self._values["smithy_build_options"] = smithy_build_options

    @builtins.property
    def service_name(self) -> "SmithyServiceName":
        '''(experimental) Smithy service name.

        :stability: experimental
        '''
        result = self._values.get("service_name")
        assert result is not None, "Required property 'service_name' is missing"
        return typing.cast("SmithyServiceName", result)

    @builtins.property
    def ignore_gradle_wrapper(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Set to false if you would like to check in your gradle wrapper.

        Do so if you would like to use a different version
        of gradle to the one provided by default

        :default: true

        :stability: experimental
        '''
        result = self._values.get("ignore_gradle_wrapper")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ignore_smithy_build_output(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Set to false if you would like to check in your smithy build output or have more fine-grained control over what is checked in, eg if you add other projections to the smithy-build.json file.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("ignore_smithy_build_output")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def smithy_build_options(self) -> typing.Optional["SmithyBuildOptions"]:
        '''(experimental) Smithy build options.

        :stability: experimental
        '''
        result = self._values.get("smithy_build_options")
        return typing.cast(typing.Optional["SmithyBuildOptions"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SmithyModelOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.SmithyProjection",
    jsii_struct_bases=[SmithyCommon],
    name_mapping={
        "imports": "imports",
        "plugins": "plugins",
        "abstract": "abstract",
        "transforms": "transforms",
    },
)
class SmithyProjection(SmithyCommon):
    def __init__(
        self,
        *,
        imports: typing.Optional[typing.Sequence[builtins.str]] = None,
        plugins: typing.Optional[typing.Mapping[builtins.str, typing.Mapping[builtins.str, typing.Any]]] = None,
        abstract: typing.Optional[builtins.bool] = None,
        transforms: typing.Optional[typing.Sequence[typing.Union["SmithyTransform", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''(experimental) A smithy build projection.

        :param imports: (experimental) List of imports.
        :param plugins: (experimental) Plugins keyed by plugin id.
        :param abstract: (experimental) Whether or not the projection is abstract.
        :param transforms: (experimental) Transforms to apply to the projection.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c5ea0995b3408d3ccc8ee5fc34a1f8f7663272a167626570de8efcb270b989c)
            check_type(argname="argument imports", value=imports, expected_type=type_hints["imports"])
            check_type(argname="argument plugins", value=plugins, expected_type=type_hints["plugins"])
            check_type(argname="argument abstract", value=abstract, expected_type=type_hints["abstract"])
            check_type(argname="argument transforms", value=transforms, expected_type=type_hints["transforms"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if imports is not None:
            self._values["imports"] = imports
        if plugins is not None:
            self._values["plugins"] = plugins
        if abstract is not None:
            self._values["abstract"] = abstract
        if transforms is not None:
            self._values["transforms"] = transforms

    @builtins.property
    def imports(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of imports.

        :stability: experimental
        '''
        result = self._values.get("imports")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def plugins(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Mapping[builtins.str, typing.Any]]]:
        '''(experimental) Plugins keyed by plugin id.

        :stability: experimental
        '''
        result = self._values.get("plugins")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Mapping[builtins.str, typing.Any]]], result)

    @builtins.property
    def abstract(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether or not the projection is abstract.

        :stability: experimental
        '''
        result = self._values.get("abstract")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def transforms(self) -> typing.Optional[typing.List["SmithyTransform"]]:
        '''(experimental) Transforms to apply to the projection.

        :stability: experimental
        '''
        result = self._values.get("transforms")
        return typing.cast(typing.Optional[typing.List["SmithyTransform"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SmithyProjection(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.SmithyServiceName",
    jsii_struct_bases=[],
    name_mapping={"namespace": "namespace", "service_name": "serviceName"},
)
class SmithyServiceName:
    def __init__(self, *, namespace: builtins.str, service_name: builtins.str) -> None:
        '''(experimental) Represents a fully qualified name of a Smithy service.

        :param namespace: (experimental) The service namespace. Nested namespaces are separated by '.', for example com.company
        :param service_name: (experimental) The service name. Should be PascalCase, for example HelloService

        :see: https://awslabs.github.io/smithy/2.0/spec/service-types.html
        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33167c5a545168279a3c6fd39d00c6b82f7fe43cb1586a4257803dd35a4a0365)
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument service_name", value=service_name, expected_type=type_hints["service_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "namespace": namespace,
            "service_name": service_name,
        }

    @builtins.property
    def namespace(self) -> builtins.str:
        '''(experimental) The service namespace.

        Nested namespaces are separated by '.', for example com.company

        :see: https://awslabs.github.io/smithy/2.0/spec/model.html#shape-id
        :stability: experimental
        '''
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def service_name(self) -> builtins.str:
        '''(experimental) The service name.

        Should be PascalCase, for example HelloService

        :see: https://awslabs.github.io/smithy/2.0/spec/model.html#shape-id
        :stability: experimental
        '''
        result = self._values.get("service_name")
        assert result is not None, "Required property 'service_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SmithyServiceName(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.SmithyTransform",
    jsii_struct_bases=[],
    name_mapping={"args": "args", "name": "name"},
)
class SmithyTransform:
    def __init__(
        self,
        *,
        args: typing.Mapping[builtins.str, typing.Any],
        name: builtins.str,
    ) -> None:
        '''(experimental) A smithy build transform.

        :param args: (experimental) Arguments for the transform.
        :param name: (experimental) Name of the transform.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4424e16fdd9894bdf9f73356687f8b13ded16ea8986897f93021567a26e01262)
            check_type(argname="argument args", value=args, expected_type=type_hints["args"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "args": args,
            "name": name,
        }

    @builtins.property
    def args(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''(experimental) Arguments for the transform.

        :stability: experimental
        '''
        result = self._values.get("args")
        assert result is not None, "Required property 'args' is missing"
        return typing.cast(typing.Mapping[builtins.str, typing.Any], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) Name of the transform.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SmithyTransform(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.TypeSafeApiIntegration",
    jsii_struct_bases=[],
    name_mapping={"integration": "integration", "authorizer": "authorizer"},
)
class TypeSafeApiIntegration:
    def __init__(
        self,
        *,
        integration: Integration,
        authorizer: typing.Optional[Authorizer] = None,
    ) -> None:
        '''(experimental) Defines an integration for an individual API operation.

        :param integration: (experimental) The lambda function to service the api operation.
        :param authorizer: (experimental) The authorizer to use for this api operation (overrides the default).

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6aac208a4d52a45aa5a05fdd9df9236f624116cf700032ca2ec93451ea1ee14c)
            check_type(argname="argument integration", value=integration, expected_type=type_hints["integration"])
            check_type(argname="argument authorizer", value=authorizer, expected_type=type_hints["authorizer"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "integration": integration,
        }
        if authorizer is not None:
            self._values["authorizer"] = authorizer

    @builtins.property
    def integration(self) -> Integration:
        '''(experimental) The lambda function to service the api operation.

        :stability: experimental
        '''
        result = self._values.get("integration")
        assert result is not None, "Required property 'integration' is missing"
        return typing.cast(Integration, result)

    @builtins.property
    def authorizer(self) -> typing.Optional[Authorizer]:
        '''(experimental) The authorizer to use for this api operation (overrides the default).

        :stability: experimental
        '''
        result = self._values.get("authorizer")
        return typing.cast(typing.Optional[Authorizer], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TypeSafeApiIntegration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TypeSafeApiModelProject(
    _projen_04054675.Project,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-prototyping-sdk/type-safe-api.TypeSafeApiModelProject",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        *,
        model_language: ModelLanguage,
        model_options: typing.Union[ModelOptions, typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        commit_generated: typing.Optional[builtins.bool] = None,
        git_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        git_options: typing.Optional[typing.Union[_projen_04054675.GitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        logging: typing.Optional[typing.Union[_projen_04054675.LoggerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[_projen_04054675.Project] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[typing.Union[_projen_04054675.ProjenrcJsonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        renovatebot: typing.Optional[builtins.bool] = None,
        renovatebot_options: typing.Optional[typing.Union[_projen_04054675.RenovatebotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param model_language: 
        :param model_options: 
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param commit_generated: (experimental) Whether to commit the managed files by default. Default: true
        :param git_ignore_options: (experimental) Configuration options for .gitignore file.
        :param git_options: (experimental) Configuration options for git.
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param renovatebot: (experimental) Use renovatebot to handle dependency upgrades. Default: false
        :param renovatebot_options: (experimental) Options for renovatebot. Default: - default options

        :stability: experimental
        '''
        options = TypeSafeApiModelProjectOptions(
            model_language=model_language,
            model_options=model_options,
            name=name,
            commit_generated=commit_generated,
            git_ignore_options=git_ignore_options,
            git_options=git_options,
            logging=logging,
            outdir=outdir,
            parent=parent,
            projen_command=projen_command,
            projenrc_json=projenrc_json,
            projenrc_json_options=projenrc_json_options,
            renovatebot=renovatebot,
            renovatebot_options=renovatebot_options,
        )

        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="generateTask")
    def generate_task(self) -> _projen_04054675.Task:
        '''(experimental) Reference to the task used for generating the final bundled OpenAPI specification.

        :stability: experimental
        '''
        return typing.cast(_projen_04054675.Task, jsii.get(self, "generateTask"))

    @builtins.property
    @jsii.member(jsii_name="parsedSpecFile")
    def parsed_spec_file(self) -> builtins.str:
        '''(experimental) Name of the final bundled OpenAPI specification.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "parsedSpecFile"))

    @builtins.property
    @jsii.member(jsii_name="openapi")
    def openapi(self) -> typing.Optional[OpenApiDefinition]:
        '''(experimental) Reference to the OpenAPI definition component.

        Will be defined if the model language is OpenAPI

        :stability: experimental
        '''
        return typing.cast(typing.Optional[OpenApiDefinition], jsii.get(self, "openapi"))

    @builtins.property
    @jsii.member(jsii_name="smithy")
    def smithy(self) -> typing.Optional[SmithyDefinition]:
        '''(experimental) Reference to the Smithy definition component.

        Will be defined if the model language is Smithy

        :stability: experimental
        '''
        return typing.cast(typing.Optional[SmithyDefinition], jsii.get(self, "smithy"))


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.TypeSafeApiModelProjectOptions",
    jsii_struct_bases=[_projen_04054675.ProjectOptions],
    name_mapping={
        "name": "name",
        "commit_generated": "commitGenerated",
        "git_ignore_options": "gitIgnoreOptions",
        "git_options": "gitOptions",
        "logging": "logging",
        "outdir": "outdir",
        "parent": "parent",
        "projen_command": "projenCommand",
        "projenrc_json": "projenrcJson",
        "projenrc_json_options": "projenrcJsonOptions",
        "renovatebot": "renovatebot",
        "renovatebot_options": "renovatebotOptions",
        "model_language": "modelLanguage",
        "model_options": "modelOptions",
    },
)
class TypeSafeApiModelProjectOptions(_projen_04054675.ProjectOptions):
    def __init__(
        self,
        *,
        name: builtins.str,
        commit_generated: typing.Optional[builtins.bool] = None,
        git_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        git_options: typing.Optional[typing.Union[_projen_04054675.GitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        logging: typing.Optional[typing.Union[_projen_04054675.LoggerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[_projen_04054675.Project] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[typing.Union[_projen_04054675.ProjenrcJsonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        renovatebot: typing.Optional[builtins.bool] = None,
        renovatebot_options: typing.Optional[typing.Union[_projen_04054675.RenovatebotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        model_language: ModelLanguage,
        model_options: typing.Union[ModelOptions, typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param commit_generated: (experimental) Whether to commit the managed files by default. Default: true
        :param git_ignore_options: (experimental) Configuration options for .gitignore file.
        :param git_options: (experimental) Configuration options for git.
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param renovatebot: (experimental) Use renovatebot to handle dependency upgrades. Default: false
        :param renovatebot_options: (experimental) Options for renovatebot. Default: - default options
        :param model_language: 
        :param model_options: 

        :stability: experimental
        '''
        if isinstance(git_ignore_options, dict):
            git_ignore_options = _projen_04054675.IgnoreFileOptions(**git_ignore_options)
        if isinstance(git_options, dict):
            git_options = _projen_04054675.GitOptions(**git_options)
        if isinstance(logging, dict):
            logging = _projen_04054675.LoggerOptions(**logging)
        if isinstance(projenrc_json_options, dict):
            projenrc_json_options = _projen_04054675.ProjenrcJsonOptions(**projenrc_json_options)
        if isinstance(renovatebot_options, dict):
            renovatebot_options = _projen_04054675.RenovatebotOptions(**renovatebot_options)
        if isinstance(model_options, dict):
            model_options = ModelOptions(**model_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab9fbe8ba5379dfe513c8876edcc903cdd8e15a6de4c21aa838dc6c6c7b2402a)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument commit_generated", value=commit_generated, expected_type=type_hints["commit_generated"])
            check_type(argname="argument git_ignore_options", value=git_ignore_options, expected_type=type_hints["git_ignore_options"])
            check_type(argname="argument git_options", value=git_options, expected_type=type_hints["git_options"])
            check_type(argname="argument logging", value=logging, expected_type=type_hints["logging"])
            check_type(argname="argument outdir", value=outdir, expected_type=type_hints["outdir"])
            check_type(argname="argument parent", value=parent, expected_type=type_hints["parent"])
            check_type(argname="argument projen_command", value=projen_command, expected_type=type_hints["projen_command"])
            check_type(argname="argument projenrc_json", value=projenrc_json, expected_type=type_hints["projenrc_json"])
            check_type(argname="argument projenrc_json_options", value=projenrc_json_options, expected_type=type_hints["projenrc_json_options"])
            check_type(argname="argument renovatebot", value=renovatebot, expected_type=type_hints["renovatebot"])
            check_type(argname="argument renovatebot_options", value=renovatebot_options, expected_type=type_hints["renovatebot_options"])
            check_type(argname="argument model_language", value=model_language, expected_type=type_hints["model_language"])
            check_type(argname="argument model_options", value=model_options, expected_type=type_hints["model_options"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "model_language": model_language,
            "model_options": model_options,
        }
        if commit_generated is not None:
            self._values["commit_generated"] = commit_generated
        if git_ignore_options is not None:
            self._values["git_ignore_options"] = git_ignore_options
        if git_options is not None:
            self._values["git_options"] = git_options
        if logging is not None:
            self._values["logging"] = logging
        if outdir is not None:
            self._values["outdir"] = outdir
        if parent is not None:
            self._values["parent"] = parent
        if projen_command is not None:
            self._values["projen_command"] = projen_command
        if projenrc_json is not None:
            self._values["projenrc_json"] = projenrc_json
        if projenrc_json_options is not None:
            self._values["projenrc_json_options"] = projenrc_json_options
        if renovatebot is not None:
            self._values["renovatebot"] = renovatebot
        if renovatebot_options is not None:
            self._values["renovatebot_options"] = renovatebot_options

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) This is the name of your project.

        :default: $BASEDIR

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def commit_generated(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to commit the managed files by default.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("commit_generated")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def git_ignore_options(self) -> typing.Optional[_projen_04054675.IgnoreFileOptions]:
        '''(experimental) Configuration options for .gitignore file.

        :stability: experimental
        '''
        result = self._values.get("git_ignore_options")
        return typing.cast(typing.Optional[_projen_04054675.IgnoreFileOptions], result)

    @builtins.property
    def git_options(self) -> typing.Optional[_projen_04054675.GitOptions]:
        '''(experimental) Configuration options for git.

        :stability: experimental
        '''
        result = self._values.get("git_options")
        return typing.cast(typing.Optional[_projen_04054675.GitOptions], result)

    @builtins.property
    def logging(self) -> typing.Optional[_projen_04054675.LoggerOptions]:
        '''(experimental) Configure logging options such as verbosity.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[_projen_04054675.LoggerOptions], result)

    @builtins.property
    def outdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) The root directory of the project.

        Relative to this directory, all files are synthesized.

        If this project has a parent, this directory is relative to the parent
        directory and it cannot be the same as the parent or any of it's other
        sub-projects.

        :default: "."

        :stability: experimental
        '''
        result = self._values.get("outdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent(self) -> typing.Optional[_projen_04054675.Project]:
        '''(experimental) The parent project, if this project is part of a bigger project.

        :stability: experimental
        '''
        result = self._values.get("parent")
        return typing.cast(typing.Optional[_projen_04054675.Project], result)

    @builtins.property
    def projen_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) The shell command to use in order to run the projen CLI.

        Can be used to customize in special environments.

        :default: "npx projen"

        :stability: experimental
        '''
        result = self._values.get("projen_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projenrc_json(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("projenrc_json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_json_options(
        self,
    ) -> typing.Optional[_projen_04054675.ProjenrcJsonOptions]:
        '''(experimental) Options for .projenrc.json.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_json_options")
        return typing.cast(typing.Optional[_projen_04054675.ProjenrcJsonOptions], result)

    @builtins.property
    def renovatebot(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use renovatebot to handle dependency upgrades.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("renovatebot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def renovatebot_options(
        self,
    ) -> typing.Optional[_projen_04054675.RenovatebotOptions]:
        '''(experimental) Options for renovatebot.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("renovatebot_options")
        return typing.cast(typing.Optional[_projen_04054675.RenovatebotOptions], result)

    @builtins.property
    def model_language(self) -> ModelLanguage:
        '''
        :stability: experimental
        '''
        result = self._values.get("model_language")
        assert result is not None, "Required property 'model_language' is missing"
        return typing.cast(ModelLanguage, result)

    @builtins.property
    def model_options(self) -> ModelOptions:
        '''
        :stability: experimental
        '''
        result = self._values.get("model_options")
        assert result is not None, "Required property 'model_options' is missing"
        return typing.cast(ModelOptions, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TypeSafeApiModelProjectOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.TypeSafeApiOptions",
    jsii_struct_bases=[],
    name_mapping={
        "integrations": "integrations",
        "operation_lookup": "operationLookup",
        "cors_options": "corsOptions",
        "default_authorizer": "defaultAuthorizer",
    },
)
class TypeSafeApiOptions:
    def __init__(
        self,
        *,
        integrations: typing.Mapping[builtins.str, typing.Union[TypeSafeApiIntegration, typing.Dict[builtins.str, typing.Any]]],
        operation_lookup: typing.Mapping[builtins.str, typing.Union[MethodAndPath, typing.Dict[builtins.str, typing.Any]]],
        cors_options: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.CorsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        default_authorizer: typing.Optional[Authorizer] = None,
    ) -> None:
        '''(experimental) Options required alongside an Open API specification to create API Gateway resources.

        :param integrations: (experimental) A mapping of API operation to its integration.
        :param operation_lookup: (experimental) Details about each operation.
        :param cors_options: (experimental) Cross Origin Resource Sharing options for the API.
        :param default_authorizer: (experimental) The default authorizer to use for your api. When omitted, no default authorizer is used. Authorizers specified at the integration level will override this for that operation.

        :stability: experimental
        '''
        if isinstance(cors_options, dict):
            cors_options = _aws_cdk_aws_apigateway_ceddda9d.CorsOptions(**cors_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddffe68493ea33b13b142dd3a74d4b71e0e9eb563dc8d340916de145a0d0dfd3)
            check_type(argname="argument integrations", value=integrations, expected_type=type_hints["integrations"])
            check_type(argname="argument operation_lookup", value=operation_lookup, expected_type=type_hints["operation_lookup"])
            check_type(argname="argument cors_options", value=cors_options, expected_type=type_hints["cors_options"])
            check_type(argname="argument default_authorizer", value=default_authorizer, expected_type=type_hints["default_authorizer"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "integrations": integrations,
            "operation_lookup": operation_lookup,
        }
        if cors_options is not None:
            self._values["cors_options"] = cors_options
        if default_authorizer is not None:
            self._values["default_authorizer"] = default_authorizer

    @builtins.property
    def integrations(self) -> typing.Mapping[builtins.str, TypeSafeApiIntegration]:
        '''(experimental) A mapping of API operation to its integration.

        :stability: experimental
        '''
        result = self._values.get("integrations")
        assert result is not None, "Required property 'integrations' is missing"
        return typing.cast(typing.Mapping[builtins.str, TypeSafeApiIntegration], result)

    @builtins.property
    def operation_lookup(self) -> typing.Mapping[builtins.str, MethodAndPath]:
        '''(experimental) Details about each operation.

        :stability: experimental
        '''
        result = self._values.get("operation_lookup")
        assert result is not None, "Required property 'operation_lookup' is missing"
        return typing.cast(typing.Mapping[builtins.str, MethodAndPath], result)

    @builtins.property
    def cors_options(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.CorsOptions]:
        '''(experimental) Cross Origin Resource Sharing options for the API.

        :stability: experimental
        '''
        result = self._values.get("cors_options")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.CorsOptions], result)

    @builtins.property
    def default_authorizer(self) -> typing.Optional[Authorizer]:
        '''(experimental) The default authorizer to use for your api.

        When omitted, no default authorizer is used.
        Authorizers specified at the integration level will override this for that operation.

        :stability: experimental
        '''
        result = self._values.get("default_authorizer")
        return typing.cast(typing.Optional[Authorizer], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TypeSafeApiOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TypeSafeApiProject(
    _projen_04054675.Project,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-prototyping-sdk/type-safe-api.TypeSafeApiProject",
):
    '''(experimental) Project for a type-safe API, defined using Smithy or OpenAPI.

    Generates a CDK construct to deploy your API, as well as client and server code to help build your API quickly.

    :stability: experimental
    :pjid: type-safe-api
    '''

    def __init__(
        self,
        *,
        infrastructure: typing.Union[InfrastructureConfiguration, typing.Dict[builtins.str, typing.Any]],
        model: typing.Union[ModelConfiguration, typing.Dict[builtins.str, typing.Any]],
        runtime: typing.Union[RuntimeConfiguration, typing.Dict[builtins.str, typing.Any]],
        documentation: typing.Optional[typing.Union[DocumentationConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        library: typing.Optional[typing.Union[LibraryConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        name: builtins.str,
        commit_generated: typing.Optional[builtins.bool] = None,
        git_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        git_options: typing.Optional[typing.Union[_projen_04054675.GitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        logging: typing.Optional[typing.Union[_projen_04054675.LoggerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[_projen_04054675.Project] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[typing.Union[_projen_04054675.ProjenrcJsonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        renovatebot: typing.Optional[builtins.bool] = None,
        renovatebot_options: typing.Optional[typing.Union[_projen_04054675.RenovatebotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param infrastructure: (experimental) Configuration for generated infrastructure.
        :param model: (experimental) Configuration for the API model.
        :param runtime: (experimental) Configuration for generated runtime projects (containing types, clients and server code).
        :param documentation: (experimental) Configuration for generated documentation.
        :param library: (experimental) Configuration for generated libraries. Libraries are projects which are generated from your model, but are not fully-fledged runtimes, for example react hooks or clients in languages that aren't supported as runtimes.
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param commit_generated: (experimental) Whether to commit the managed files by default. Default: true
        :param git_ignore_options: (experimental) Configuration options for .gitignore file.
        :param git_options: (experimental) Configuration options for git.
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param renovatebot: (experimental) Use renovatebot to handle dependency upgrades. Default: false
        :param renovatebot_options: (experimental) Options for renovatebot. Default: - default options

        :stability: experimental
        '''
        options = TypeSafeApiProjectOptions(
            infrastructure=infrastructure,
            model=model,
            runtime=runtime,
            documentation=documentation,
            library=library,
            name=name,
            commit_generated=commit_generated,
            git_ignore_options=git_ignore_options,
            git_options=git_options,
            logging=logging,
            outdir=outdir,
            parent=parent,
            projen_command=projen_command,
            projenrc_json=projenrc_json,
            projenrc_json_options=projenrc_json_options,
            renovatebot=renovatebot,
            renovatebot_options=renovatebot_options,
        )

        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="infrastructure")
    def infrastructure(self) -> GeneratedCodeProjects:
        '''(experimental) Generated infrastructure projects.

        Only the property corresponding to ``infrastructure.language`` will be defined.

        :stability: experimental
        '''
        return typing.cast(GeneratedCodeProjects, jsii.get(self, "infrastructure"))

    @builtins.property
    @jsii.member(jsii_name="library")
    def library(self) -> GeneratedLibraryProjects:
        '''(experimental) Generated library projects.

        Only the properties corresponding to specified ``library.libraries`` will be defined.

        :stability: experimental
        '''
        return typing.cast(GeneratedLibraryProjects, jsii.get(self, "library"))

    @builtins.property
    @jsii.member(jsii_name="model")
    def model(self) -> TypeSafeApiModelProject:
        '''(experimental) Project for the api model.

        :stability: experimental
        '''
        return typing.cast(TypeSafeApiModelProject, jsii.get(self, "model"))

    @builtins.property
    @jsii.member(jsii_name="runtime")
    def runtime(self) -> GeneratedCodeProjects:
        '''(experimental) Generated runtime projects.

        When ``runtime.languages`` includes the corresponding language, the project can be
        assumed to be defined.

        :stability: experimental
        '''
        return typing.cast(GeneratedCodeProjects, jsii.get(self, "runtime"))


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.TypeSafeApiProjectOptions",
    jsii_struct_bases=[_projen_04054675.ProjectOptions],
    name_mapping={
        "name": "name",
        "commit_generated": "commitGenerated",
        "git_ignore_options": "gitIgnoreOptions",
        "git_options": "gitOptions",
        "logging": "logging",
        "outdir": "outdir",
        "parent": "parent",
        "projen_command": "projenCommand",
        "projenrc_json": "projenrcJson",
        "projenrc_json_options": "projenrcJsonOptions",
        "renovatebot": "renovatebot",
        "renovatebot_options": "renovatebotOptions",
        "infrastructure": "infrastructure",
        "model": "model",
        "runtime": "runtime",
        "documentation": "documentation",
        "library": "library",
    },
)
class TypeSafeApiProjectOptions(_projen_04054675.ProjectOptions):
    def __init__(
        self,
        *,
        name: builtins.str,
        commit_generated: typing.Optional[builtins.bool] = None,
        git_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        git_options: typing.Optional[typing.Union[_projen_04054675.GitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        logging: typing.Optional[typing.Union[_projen_04054675.LoggerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[_projen_04054675.Project] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[typing.Union[_projen_04054675.ProjenrcJsonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        renovatebot: typing.Optional[builtins.bool] = None,
        renovatebot_options: typing.Optional[typing.Union[_projen_04054675.RenovatebotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        infrastructure: typing.Union[InfrastructureConfiguration, typing.Dict[builtins.str, typing.Any]],
        model: typing.Union[ModelConfiguration, typing.Dict[builtins.str, typing.Any]],
        runtime: typing.Union[RuntimeConfiguration, typing.Dict[builtins.str, typing.Any]],
        documentation: typing.Optional[typing.Union[DocumentationConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        library: typing.Optional[typing.Union[LibraryConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Options for the TypeSafeApiProject.

        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param commit_generated: (experimental) Whether to commit the managed files by default. Default: true
        :param git_ignore_options: (experimental) Configuration options for .gitignore file.
        :param git_options: (experimental) Configuration options for git.
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param renovatebot: (experimental) Use renovatebot to handle dependency upgrades. Default: false
        :param renovatebot_options: (experimental) Options for renovatebot. Default: - default options
        :param infrastructure: (experimental) Configuration for generated infrastructure.
        :param model: (experimental) Configuration for the API model.
        :param runtime: (experimental) Configuration for generated runtime projects (containing types, clients and server code).
        :param documentation: (experimental) Configuration for generated documentation.
        :param library: (experimental) Configuration for generated libraries. Libraries are projects which are generated from your model, but are not fully-fledged runtimes, for example react hooks or clients in languages that aren't supported as runtimes.

        :stability: experimental
        '''
        if isinstance(git_ignore_options, dict):
            git_ignore_options = _projen_04054675.IgnoreFileOptions(**git_ignore_options)
        if isinstance(git_options, dict):
            git_options = _projen_04054675.GitOptions(**git_options)
        if isinstance(logging, dict):
            logging = _projen_04054675.LoggerOptions(**logging)
        if isinstance(projenrc_json_options, dict):
            projenrc_json_options = _projen_04054675.ProjenrcJsonOptions(**projenrc_json_options)
        if isinstance(renovatebot_options, dict):
            renovatebot_options = _projen_04054675.RenovatebotOptions(**renovatebot_options)
        if isinstance(infrastructure, dict):
            infrastructure = InfrastructureConfiguration(**infrastructure)
        if isinstance(model, dict):
            model = ModelConfiguration(**model)
        if isinstance(runtime, dict):
            runtime = RuntimeConfiguration(**runtime)
        if isinstance(documentation, dict):
            documentation = DocumentationConfiguration(**documentation)
        if isinstance(library, dict):
            library = LibraryConfiguration(**library)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abde6fa90ff9fea9e430aaca82f0c910c5ecc24d1205ba19958f47080d5b15fb)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument commit_generated", value=commit_generated, expected_type=type_hints["commit_generated"])
            check_type(argname="argument git_ignore_options", value=git_ignore_options, expected_type=type_hints["git_ignore_options"])
            check_type(argname="argument git_options", value=git_options, expected_type=type_hints["git_options"])
            check_type(argname="argument logging", value=logging, expected_type=type_hints["logging"])
            check_type(argname="argument outdir", value=outdir, expected_type=type_hints["outdir"])
            check_type(argname="argument parent", value=parent, expected_type=type_hints["parent"])
            check_type(argname="argument projen_command", value=projen_command, expected_type=type_hints["projen_command"])
            check_type(argname="argument projenrc_json", value=projenrc_json, expected_type=type_hints["projenrc_json"])
            check_type(argname="argument projenrc_json_options", value=projenrc_json_options, expected_type=type_hints["projenrc_json_options"])
            check_type(argname="argument renovatebot", value=renovatebot, expected_type=type_hints["renovatebot"])
            check_type(argname="argument renovatebot_options", value=renovatebot_options, expected_type=type_hints["renovatebot_options"])
            check_type(argname="argument infrastructure", value=infrastructure, expected_type=type_hints["infrastructure"])
            check_type(argname="argument model", value=model, expected_type=type_hints["model"])
            check_type(argname="argument runtime", value=runtime, expected_type=type_hints["runtime"])
            check_type(argname="argument documentation", value=documentation, expected_type=type_hints["documentation"])
            check_type(argname="argument library", value=library, expected_type=type_hints["library"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "infrastructure": infrastructure,
            "model": model,
            "runtime": runtime,
        }
        if commit_generated is not None:
            self._values["commit_generated"] = commit_generated
        if git_ignore_options is not None:
            self._values["git_ignore_options"] = git_ignore_options
        if git_options is not None:
            self._values["git_options"] = git_options
        if logging is not None:
            self._values["logging"] = logging
        if outdir is not None:
            self._values["outdir"] = outdir
        if parent is not None:
            self._values["parent"] = parent
        if projen_command is not None:
            self._values["projen_command"] = projen_command
        if projenrc_json is not None:
            self._values["projenrc_json"] = projenrc_json
        if projenrc_json_options is not None:
            self._values["projenrc_json_options"] = projenrc_json_options
        if renovatebot is not None:
            self._values["renovatebot"] = renovatebot
        if renovatebot_options is not None:
            self._values["renovatebot_options"] = renovatebot_options
        if documentation is not None:
            self._values["documentation"] = documentation
        if library is not None:
            self._values["library"] = library

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) This is the name of your project.

        :default: $BASEDIR

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def commit_generated(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to commit the managed files by default.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("commit_generated")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def git_ignore_options(self) -> typing.Optional[_projen_04054675.IgnoreFileOptions]:
        '''(experimental) Configuration options for .gitignore file.

        :stability: experimental
        '''
        result = self._values.get("git_ignore_options")
        return typing.cast(typing.Optional[_projen_04054675.IgnoreFileOptions], result)

    @builtins.property
    def git_options(self) -> typing.Optional[_projen_04054675.GitOptions]:
        '''(experimental) Configuration options for git.

        :stability: experimental
        '''
        result = self._values.get("git_options")
        return typing.cast(typing.Optional[_projen_04054675.GitOptions], result)

    @builtins.property
    def logging(self) -> typing.Optional[_projen_04054675.LoggerOptions]:
        '''(experimental) Configure logging options such as verbosity.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[_projen_04054675.LoggerOptions], result)

    @builtins.property
    def outdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) The root directory of the project.

        Relative to this directory, all files are synthesized.

        If this project has a parent, this directory is relative to the parent
        directory and it cannot be the same as the parent or any of it's other
        sub-projects.

        :default: "."

        :stability: experimental
        '''
        result = self._values.get("outdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent(self) -> typing.Optional[_projen_04054675.Project]:
        '''(experimental) The parent project, if this project is part of a bigger project.

        :stability: experimental
        '''
        result = self._values.get("parent")
        return typing.cast(typing.Optional[_projen_04054675.Project], result)

    @builtins.property
    def projen_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) The shell command to use in order to run the projen CLI.

        Can be used to customize in special environments.

        :default: "npx projen"

        :stability: experimental
        '''
        result = self._values.get("projen_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projenrc_json(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("projenrc_json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_json_options(
        self,
    ) -> typing.Optional[_projen_04054675.ProjenrcJsonOptions]:
        '''(experimental) Options for .projenrc.json.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_json_options")
        return typing.cast(typing.Optional[_projen_04054675.ProjenrcJsonOptions], result)

    @builtins.property
    def renovatebot(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use renovatebot to handle dependency upgrades.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("renovatebot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def renovatebot_options(
        self,
    ) -> typing.Optional[_projen_04054675.RenovatebotOptions]:
        '''(experimental) Options for renovatebot.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("renovatebot_options")
        return typing.cast(typing.Optional[_projen_04054675.RenovatebotOptions], result)

    @builtins.property
    def infrastructure(self) -> InfrastructureConfiguration:
        '''(experimental) Configuration for generated infrastructure.

        :stability: experimental
        '''
        result = self._values.get("infrastructure")
        assert result is not None, "Required property 'infrastructure' is missing"
        return typing.cast(InfrastructureConfiguration, result)

    @builtins.property
    def model(self) -> ModelConfiguration:
        '''(experimental) Configuration for the API model.

        :stability: experimental
        '''
        result = self._values.get("model")
        assert result is not None, "Required property 'model' is missing"
        return typing.cast(ModelConfiguration, result)

    @builtins.property
    def runtime(self) -> RuntimeConfiguration:
        '''(experimental) Configuration for generated runtime projects (containing types, clients and server code).

        :stability: experimental
        '''
        result = self._values.get("runtime")
        assert result is not None, "Required property 'runtime' is missing"
        return typing.cast(RuntimeConfiguration, result)

    @builtins.property
    def documentation(self) -> typing.Optional[DocumentationConfiguration]:
        '''(experimental) Configuration for generated documentation.

        :stability: experimental
        '''
        result = self._values.get("documentation")
        return typing.cast(typing.Optional[DocumentationConfiguration], result)

    @builtins.property
    def library(self) -> typing.Optional[LibraryConfiguration]:
        '''(experimental) Configuration for generated libraries.

        Libraries are projects which are generated from your model, but are not
        fully-fledged runtimes, for example react hooks or clients in languages that aren't supported as runtimes.

        :stability: experimental
        '''
        result = self._values.get("library")
        return typing.cast(typing.Optional[LibraryConfiguration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TypeSafeApiProjectOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.TypeSafeApiWebAclOptions",
    jsii_struct_bases=[],
    name_mapping={
        "cidr_allow_list": "cidrAllowList",
        "disable": "disable",
        "managed_rules": "managedRules",
    },
)
class TypeSafeApiWebAclOptions:
    def __init__(
        self,
        *,
        cidr_allow_list: typing.Optional[typing.Union[CidrAllowList, typing.Dict[builtins.str, typing.Any]]] = None,
        disable: typing.Optional[builtins.bool] = None,
        managed_rules: typing.Optional[typing.Sequence[typing.Union[ManagedRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''(experimental) Configuration for the Web ACL associated with the API.

        :param cidr_allow_list: (experimental) List of cidr ranges to allow. Default: - undefined
        :param disable: (experimental) If set to true, no WebACL will be associated with the API. You can also use this option if you would like to create your own WebACL and associate it yourself. Default: false
        :param managed_rules: (experimental) List of managed rules to apply to the web acl. Default: - [{ vendor: "AWS", name: "AWSManagedRulesCommonRuleSet" }]

        :stability: experimental
        '''
        if isinstance(cidr_allow_list, dict):
            cidr_allow_list = CidrAllowList(**cidr_allow_list)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__767125a1376366edf6341c113fbc39f6e469b47eea26e1fa3720cfc786f2d558)
            check_type(argname="argument cidr_allow_list", value=cidr_allow_list, expected_type=type_hints["cidr_allow_list"])
            check_type(argname="argument disable", value=disable, expected_type=type_hints["disable"])
            check_type(argname="argument managed_rules", value=managed_rules, expected_type=type_hints["managed_rules"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cidr_allow_list is not None:
            self._values["cidr_allow_list"] = cidr_allow_list
        if disable is not None:
            self._values["disable"] = disable
        if managed_rules is not None:
            self._values["managed_rules"] = managed_rules

    @builtins.property
    def cidr_allow_list(self) -> typing.Optional[CidrAllowList]:
        '''(experimental) List of cidr ranges to allow.

        :default: - undefined

        :stability: experimental
        '''
        result = self._values.get("cidr_allow_list")
        return typing.cast(typing.Optional[CidrAllowList], result)

    @builtins.property
    def disable(self) -> typing.Optional[builtins.bool]:
        '''(experimental) If set to true, no WebACL will be associated with the API.

        You can also use this option if you would like to create
        your own WebACL and associate it yourself.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("disable")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def managed_rules(self) -> typing.Optional[typing.List[ManagedRule]]:
        '''(experimental) List of managed rules to apply to the web acl.

        :default: - [{ vendor: "AWS", name: "AWSManagedRulesCommonRuleSet" }]

        :stability: experimental
        '''
        result = self._values.get("managed_rules")
        return typing.cast(typing.Optional[typing.List[ManagedRule]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TypeSafeApiWebAclOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TypeSafeRestApi(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-prototyping-sdk/type-safe-api.TypeSafeRestApi",
):
    '''(experimental) A construct for creating an api gateway rest api based on the definition in the OpenAPI spec.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        spec_path: builtins.str,
        web_acl_options: typing.Optional[typing.Union[TypeSafeApiWebAclOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        cloud_watch_role: typing.Optional[builtins.bool] = None,
        deploy: typing.Optional[builtins.bool] = None,
        deploy_options: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.StageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        disable_execute_api_endpoint: typing.Optional[builtins.bool] = None,
        domain_name: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.DomainNameOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        endpoint_export_name: typing.Optional[builtins.str] = None,
        endpoint_types: typing.Optional[typing.Sequence[_aws_cdk_aws_apigateway_ceddda9d.EndpointType]] = None,
        fail_on_warnings: typing.Optional[builtins.bool] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
        rest_api_name: typing.Optional[builtins.str] = None,
        retain_deployments: typing.Optional[builtins.bool] = None,
        integrations: typing.Mapping[builtins.str, typing.Union[TypeSafeApiIntegration, typing.Dict[builtins.str, typing.Any]]],
        operation_lookup: typing.Mapping[builtins.str, typing.Union[MethodAndPath, typing.Dict[builtins.str, typing.Any]]],
        cors_options: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.CorsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        default_authorizer: typing.Optional[Authorizer] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param spec_path: (experimental) Path to the JSON open api spec.
        :param web_acl_options: (experimental) Options for the AWS WAF v2 WebACL associated with the api. By default, a Web ACL with the AWS default managed rule set will be associated with the API. These options may disable or override the defaults.
        :param cloud_watch_role: Automatically configure an AWS CloudWatch role for API Gateway. Default: - false if ``@aws-cdk/aws-apigateway:disableCloudWatchRole`` is enabled, true otherwise
        :param deploy: Indicates if a Deployment should be automatically created for this API, and recreated when the API model (resources, methods) changes. Since API Gateway deployments are immutable, When this option is enabled (by default), an AWS::ApiGateway::Deployment resource will automatically created with a logical ID that hashes the API model (methods, resources and options). This means that when the model changes, the logical ID of this CloudFormation resource will change, and a new deployment will be created. If this is set, ``latestDeployment`` will refer to the ``Deployment`` object and ``deploymentStage`` will refer to a ``Stage`` that points to this deployment. To customize the stage options, use the ``deployOptions`` property. A CloudFormation Output will also be defined with the root URL endpoint of this REST API. Default: true
        :param deploy_options: Options for the API Gateway stage that will always point to the latest deployment when ``deploy`` is enabled. If ``deploy`` is disabled, this value cannot be set. Default: - Based on defaults of ``StageOptions``.
        :param description: A description of the RestApi construct. Default: - 'Automatically created by the RestApi construct'
        :param disable_execute_api_endpoint: Specifies whether clients can invoke the API using the default execute-api endpoint. To require that clients use a custom domain name to invoke the API, disable the default endpoint. Default: false
        :param domain_name: Configure a custom domain name and map it to this API. Default: - no domain name is defined, use ``addDomainName`` or directly define a ``DomainName``.
        :param endpoint_export_name: Export name for the CfnOutput containing the API endpoint. Default: - when no export name is given, output will be created without export
        :param endpoint_types: A list of the endpoint types of the API. Use this property when creating an API. Default: EndpointType.EDGE
        :param fail_on_warnings: Indicates whether to roll back the resource if a warning occurs while API Gateway is creating the RestApi resource. Default: false
        :param parameters: Custom header parameters for the request. Default: - No parameters.
        :param policy: A policy document that contains the permissions for this RestApi. Default: - No policy.
        :param rest_api_name: A name for the API Gateway RestApi resource. Default: - ID of the RestApi construct.
        :param retain_deployments: Retains old deployment resources when the API changes. This allows manually reverting stages to point to old deployments via the AWS Console. Default: false
        :param integrations: (experimental) A mapping of API operation to its integration.
        :param operation_lookup: (experimental) Details about each operation.
        :param cors_options: (experimental) Cross Origin Resource Sharing options for the API.
        :param default_authorizer: (experimental) The default authorizer to use for your api. When omitted, no default authorizer is used. Authorizers specified at the integration level will override this for that operation.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e4821d6581d103cd1939ca5166c26d862d1742c080c74994a7cd4722c1c2d19)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TypeSafeRestApiProps(
            spec_path=spec_path,
            web_acl_options=web_acl_options,
            cloud_watch_role=cloud_watch_role,
            deploy=deploy,
            deploy_options=deploy_options,
            description=description,
            disable_execute_api_endpoint=disable_execute_api_endpoint,
            domain_name=domain_name,
            endpoint_export_name=endpoint_export_name,
            endpoint_types=endpoint_types,
            fail_on_warnings=fail_on_warnings,
            parameters=parameters,
            policy=policy,
            rest_api_name=rest_api_name,
            retain_deployments=retain_deployments,
            integrations=integrations,
            operation_lookup=operation_lookup,
            cors_options=cors_options,
            default_authorizer=default_authorizer,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="api")
    def api(self) -> _aws_cdk_aws_apigateway_ceddda9d.SpecRestApi:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.SpecRestApi, jsii.get(self, "api"))

    @builtins.property
    @jsii.member(jsii_name="ipSet")
    def ip_set(self) -> typing.Optional[_aws_cdk_aws_wafv2_ceddda9d.CfnIPSet]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_wafv2_ceddda9d.CfnIPSet], jsii.get(self, "ipSet"))

    @builtins.property
    @jsii.member(jsii_name="webAcl")
    def web_acl(self) -> typing.Optional[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL], jsii.get(self, "webAcl"))

    @builtins.property
    @jsii.member(jsii_name="webAclAssociation")
    def web_acl_association(
        self,
    ) -> typing.Optional[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACLAssociation]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACLAssociation], jsii.get(self, "webAclAssociation"))


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.TypeSafeRestApiProps",
    jsii_struct_bases=[
        _aws_cdk_aws_apigateway_ceddda9d.RestApiBaseProps, TypeSafeApiOptions
    ],
    name_mapping={
        "cloud_watch_role": "cloudWatchRole",
        "deploy": "deploy",
        "deploy_options": "deployOptions",
        "description": "description",
        "disable_execute_api_endpoint": "disableExecuteApiEndpoint",
        "domain_name": "domainName",
        "endpoint_export_name": "endpointExportName",
        "endpoint_types": "endpointTypes",
        "fail_on_warnings": "failOnWarnings",
        "parameters": "parameters",
        "policy": "policy",
        "rest_api_name": "restApiName",
        "retain_deployments": "retainDeployments",
        "integrations": "integrations",
        "operation_lookup": "operationLookup",
        "cors_options": "corsOptions",
        "default_authorizer": "defaultAuthorizer",
        "spec_path": "specPath",
        "web_acl_options": "webAclOptions",
    },
)
class TypeSafeRestApiProps(
    _aws_cdk_aws_apigateway_ceddda9d.RestApiBaseProps,
    TypeSafeApiOptions,
):
    def __init__(
        self,
        *,
        cloud_watch_role: typing.Optional[builtins.bool] = None,
        deploy: typing.Optional[builtins.bool] = None,
        deploy_options: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.StageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        disable_execute_api_endpoint: typing.Optional[builtins.bool] = None,
        domain_name: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.DomainNameOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        endpoint_export_name: typing.Optional[builtins.str] = None,
        endpoint_types: typing.Optional[typing.Sequence[_aws_cdk_aws_apigateway_ceddda9d.EndpointType]] = None,
        fail_on_warnings: typing.Optional[builtins.bool] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
        rest_api_name: typing.Optional[builtins.str] = None,
        retain_deployments: typing.Optional[builtins.bool] = None,
        integrations: typing.Mapping[builtins.str, typing.Union[TypeSafeApiIntegration, typing.Dict[builtins.str, typing.Any]]],
        operation_lookup: typing.Mapping[builtins.str, typing.Union[MethodAndPath, typing.Dict[builtins.str, typing.Any]]],
        cors_options: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.CorsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        default_authorizer: typing.Optional[Authorizer] = None,
        spec_path: builtins.str,
        web_acl_options: typing.Optional[typing.Union[TypeSafeApiWebAclOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Configuration for the TypeSafeRestApi construct.

        :param cloud_watch_role: Automatically configure an AWS CloudWatch role for API Gateway. Default: - false if ``@aws-cdk/aws-apigateway:disableCloudWatchRole`` is enabled, true otherwise
        :param deploy: Indicates if a Deployment should be automatically created for this API, and recreated when the API model (resources, methods) changes. Since API Gateway deployments are immutable, When this option is enabled (by default), an AWS::ApiGateway::Deployment resource will automatically created with a logical ID that hashes the API model (methods, resources and options). This means that when the model changes, the logical ID of this CloudFormation resource will change, and a new deployment will be created. If this is set, ``latestDeployment`` will refer to the ``Deployment`` object and ``deploymentStage`` will refer to a ``Stage`` that points to this deployment. To customize the stage options, use the ``deployOptions`` property. A CloudFormation Output will also be defined with the root URL endpoint of this REST API. Default: true
        :param deploy_options: Options for the API Gateway stage that will always point to the latest deployment when ``deploy`` is enabled. If ``deploy`` is disabled, this value cannot be set. Default: - Based on defaults of ``StageOptions``.
        :param description: A description of the RestApi construct. Default: - 'Automatically created by the RestApi construct'
        :param disable_execute_api_endpoint: Specifies whether clients can invoke the API using the default execute-api endpoint. To require that clients use a custom domain name to invoke the API, disable the default endpoint. Default: false
        :param domain_name: Configure a custom domain name and map it to this API. Default: - no domain name is defined, use ``addDomainName`` or directly define a ``DomainName``.
        :param endpoint_export_name: Export name for the CfnOutput containing the API endpoint. Default: - when no export name is given, output will be created without export
        :param endpoint_types: A list of the endpoint types of the API. Use this property when creating an API. Default: EndpointType.EDGE
        :param fail_on_warnings: Indicates whether to roll back the resource if a warning occurs while API Gateway is creating the RestApi resource. Default: false
        :param parameters: Custom header parameters for the request. Default: - No parameters.
        :param policy: A policy document that contains the permissions for this RestApi. Default: - No policy.
        :param rest_api_name: A name for the API Gateway RestApi resource. Default: - ID of the RestApi construct.
        :param retain_deployments: Retains old deployment resources when the API changes. This allows manually reverting stages to point to old deployments via the AWS Console. Default: false
        :param integrations: (experimental) A mapping of API operation to its integration.
        :param operation_lookup: (experimental) Details about each operation.
        :param cors_options: (experimental) Cross Origin Resource Sharing options for the API.
        :param default_authorizer: (experimental) The default authorizer to use for your api. When omitted, no default authorizer is used. Authorizers specified at the integration level will override this for that operation.
        :param spec_path: (experimental) Path to the JSON open api spec.
        :param web_acl_options: (experimental) Options for the AWS WAF v2 WebACL associated with the api. By default, a Web ACL with the AWS default managed rule set will be associated with the API. These options may disable or override the defaults.

        :stability: experimental
        '''
        if isinstance(deploy_options, dict):
            deploy_options = _aws_cdk_aws_apigateway_ceddda9d.StageOptions(**deploy_options)
        if isinstance(domain_name, dict):
            domain_name = _aws_cdk_aws_apigateway_ceddda9d.DomainNameOptions(**domain_name)
        if isinstance(cors_options, dict):
            cors_options = _aws_cdk_aws_apigateway_ceddda9d.CorsOptions(**cors_options)
        if isinstance(web_acl_options, dict):
            web_acl_options = TypeSafeApiWebAclOptions(**web_acl_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6abf7110490d9869d975a50b9fe29f98259a9a230be2bbcde1c8e0ea1fd15771)
            check_type(argname="argument cloud_watch_role", value=cloud_watch_role, expected_type=type_hints["cloud_watch_role"])
            check_type(argname="argument deploy", value=deploy, expected_type=type_hints["deploy"])
            check_type(argname="argument deploy_options", value=deploy_options, expected_type=type_hints["deploy_options"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument disable_execute_api_endpoint", value=disable_execute_api_endpoint, expected_type=type_hints["disable_execute_api_endpoint"])
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument endpoint_export_name", value=endpoint_export_name, expected_type=type_hints["endpoint_export_name"])
            check_type(argname="argument endpoint_types", value=endpoint_types, expected_type=type_hints["endpoint_types"])
            check_type(argname="argument fail_on_warnings", value=fail_on_warnings, expected_type=type_hints["fail_on_warnings"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument policy", value=policy, expected_type=type_hints["policy"])
            check_type(argname="argument rest_api_name", value=rest_api_name, expected_type=type_hints["rest_api_name"])
            check_type(argname="argument retain_deployments", value=retain_deployments, expected_type=type_hints["retain_deployments"])
            check_type(argname="argument integrations", value=integrations, expected_type=type_hints["integrations"])
            check_type(argname="argument operation_lookup", value=operation_lookup, expected_type=type_hints["operation_lookup"])
            check_type(argname="argument cors_options", value=cors_options, expected_type=type_hints["cors_options"])
            check_type(argname="argument default_authorizer", value=default_authorizer, expected_type=type_hints["default_authorizer"])
            check_type(argname="argument spec_path", value=spec_path, expected_type=type_hints["spec_path"])
            check_type(argname="argument web_acl_options", value=web_acl_options, expected_type=type_hints["web_acl_options"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "integrations": integrations,
            "operation_lookup": operation_lookup,
            "spec_path": spec_path,
        }
        if cloud_watch_role is not None:
            self._values["cloud_watch_role"] = cloud_watch_role
        if deploy is not None:
            self._values["deploy"] = deploy
        if deploy_options is not None:
            self._values["deploy_options"] = deploy_options
        if description is not None:
            self._values["description"] = description
        if disable_execute_api_endpoint is not None:
            self._values["disable_execute_api_endpoint"] = disable_execute_api_endpoint
        if domain_name is not None:
            self._values["domain_name"] = domain_name
        if endpoint_export_name is not None:
            self._values["endpoint_export_name"] = endpoint_export_name
        if endpoint_types is not None:
            self._values["endpoint_types"] = endpoint_types
        if fail_on_warnings is not None:
            self._values["fail_on_warnings"] = fail_on_warnings
        if parameters is not None:
            self._values["parameters"] = parameters
        if policy is not None:
            self._values["policy"] = policy
        if rest_api_name is not None:
            self._values["rest_api_name"] = rest_api_name
        if retain_deployments is not None:
            self._values["retain_deployments"] = retain_deployments
        if cors_options is not None:
            self._values["cors_options"] = cors_options
        if default_authorizer is not None:
            self._values["default_authorizer"] = default_authorizer
        if web_acl_options is not None:
            self._values["web_acl_options"] = web_acl_options

    @builtins.property
    def cloud_watch_role(self) -> typing.Optional[builtins.bool]:
        '''Automatically configure an AWS CloudWatch role for API Gateway.

        :default: - false if ``@aws-cdk/aws-apigateway:disableCloudWatchRole`` is enabled, true otherwise
        '''
        result = self._values.get("cloud_watch_role")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def deploy(self) -> typing.Optional[builtins.bool]:
        '''Indicates if a Deployment should be automatically created for this API, and recreated when the API model (resources, methods) changes.

        Since API Gateway deployments are immutable, When this option is enabled
        (by default), an AWS::ApiGateway::Deployment resource will automatically
        created with a logical ID that hashes the API model (methods, resources
        and options). This means that when the model changes, the logical ID of
        this CloudFormation resource will change, and a new deployment will be
        created.

        If this is set, ``latestDeployment`` will refer to the ``Deployment`` object
        and ``deploymentStage`` will refer to a ``Stage`` that points to this
        deployment. To customize the stage options, use the ``deployOptions``
        property.

        A CloudFormation Output will also be defined with the root URL endpoint
        of this REST API.

        :default: true
        '''
        result = self._values.get("deploy")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def deploy_options(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.StageOptions]:
        '''Options for the API Gateway stage that will always point to the latest deployment when ``deploy`` is enabled.

        If ``deploy`` is disabled,
        this value cannot be set.

        :default: - Based on defaults of ``StageOptions``.
        '''
        result = self._values.get("deploy_options")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.StageOptions], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the RestApi construct.

        :default: - 'Automatically created by the RestApi construct'
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_execute_api_endpoint(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether clients can invoke the API using the default execute-api endpoint.

        To require that clients use a custom domain name to invoke the
        API, disable the default endpoint.

        :default: false

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-restapi.html
        '''
        result = self._values.get("disable_execute_api_endpoint")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def domain_name(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.DomainNameOptions]:
        '''Configure a custom domain name and map it to this API.

        :default: - no domain name is defined, use ``addDomainName`` or directly define a ``DomainName``.
        '''
        result = self._values.get("domain_name")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.DomainNameOptions], result)

    @builtins.property
    def endpoint_export_name(self) -> typing.Optional[builtins.str]:
        '''Export name for the CfnOutput containing the API endpoint.

        :default: - when no export name is given, output will be created without export
        '''
        result = self._values.get("endpoint_export_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endpoint_types(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_apigateway_ceddda9d.EndpointType]]:
        '''A list of the endpoint types of the API.

        Use this property when creating
        an API.

        :default: EndpointType.EDGE
        '''
        result = self._values.get("endpoint_types")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_apigateway_ceddda9d.EndpointType]], result)

    @builtins.property
    def fail_on_warnings(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether to roll back the resource if a warning occurs while API Gateway is creating the RestApi resource.

        :default: false
        '''
        result = self._values.get("fail_on_warnings")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Custom header parameters for the request.

        :default: - No parameters.

        :see: https://docs.aws.amazon.com/cli/latest/reference/apigateway/import-rest-api.html
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def policy(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument]:
        '''A policy document that contains the permissions for this RestApi.

        :default: - No policy.
        '''
        result = self._values.get("policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument], result)

    @builtins.property
    def rest_api_name(self) -> typing.Optional[builtins.str]:
        '''A name for the API Gateway RestApi resource.

        :default: - ID of the RestApi construct.
        '''
        result = self._values.get("rest_api_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def retain_deployments(self) -> typing.Optional[builtins.bool]:
        '''Retains old deployment resources when the API changes.

        This allows
        manually reverting stages to point to old deployments via the AWS
        Console.

        :default: false
        '''
        result = self._values.get("retain_deployments")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def integrations(self) -> typing.Mapping[builtins.str, TypeSafeApiIntegration]:
        '''(experimental) A mapping of API operation to its integration.

        :stability: experimental
        '''
        result = self._values.get("integrations")
        assert result is not None, "Required property 'integrations' is missing"
        return typing.cast(typing.Mapping[builtins.str, TypeSafeApiIntegration], result)

    @builtins.property
    def operation_lookup(self) -> typing.Mapping[builtins.str, MethodAndPath]:
        '''(experimental) Details about each operation.

        :stability: experimental
        '''
        result = self._values.get("operation_lookup")
        assert result is not None, "Required property 'operation_lookup' is missing"
        return typing.cast(typing.Mapping[builtins.str, MethodAndPath], result)

    @builtins.property
    def cors_options(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.CorsOptions]:
        '''(experimental) Cross Origin Resource Sharing options for the API.

        :stability: experimental
        '''
        result = self._values.get("cors_options")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.CorsOptions], result)

    @builtins.property
    def default_authorizer(self) -> typing.Optional[Authorizer]:
        '''(experimental) The default authorizer to use for your api.

        When omitted, no default authorizer is used.
        Authorizers specified at the integration level will override this for that operation.

        :stability: experimental
        '''
        result = self._values.get("default_authorizer")
        return typing.cast(typing.Optional[Authorizer], result)

    @builtins.property
    def spec_path(self) -> builtins.str:
        '''(experimental) Path to the JSON open api spec.

        :stability: experimental
        '''
        result = self._values.get("spec_path")
        assert result is not None, "Required property 'spec_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def web_acl_options(self) -> typing.Optional[TypeSafeApiWebAclOptions]:
        '''(experimental) Options for the AWS WAF v2 WebACL associated with the api.

        By default, a Web ACL with the AWS default managed
        rule set will be associated with the API. These options may disable or override the defaults.

        :stability: experimental
        '''
        result = self._values.get("web_acl_options")
        return typing.cast(typing.Optional[TypeSafeApiWebAclOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TypeSafeRestApiProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.IntegrationGrantProps",
    jsii_struct_bases=[MethodAndPath],
    name_mapping={
        "method": "method",
        "path": "path",
        "api": "api",
        "operation_id": "operationId",
        "scope": "scope",
    },
)
class IntegrationGrantProps(MethodAndPath):
    def __init__(
        self,
        *,
        method: builtins.str,
        path: builtins.str,
        api: _aws_cdk_aws_apigateway_ceddda9d.SpecRestApi,
        operation_id: builtins.str,
        scope: _constructs_77d1e7e8.Construct,
    ) -> None:
        '''(experimental) Properties for granting the API access to invoke the operation.

        :param method: (experimental) The http method of this operation.
        :param path: (experimental) The path of this operation in the api.
        :param api: (experimental) The api to grant permissions for.
        :param operation_id: (experimental) The ID of the operation for which permissions are being granted.
        :param scope: (experimental) The scope in which permission resources can be created.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a68568c451e2693b26c89a6bdf98c3e1d54546a0033bfd04bfa581e39ee47c28)
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument api", value=api, expected_type=type_hints["api"])
            check_type(argname="argument operation_id", value=operation_id, expected_type=type_hints["operation_id"])
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "method": method,
            "path": path,
            "api": api,
            "operation_id": operation_id,
            "scope": scope,
        }

    @builtins.property
    def method(self) -> builtins.str:
        '''(experimental) The http method of this operation.

        :stability: experimental
        '''
        result = self._values.get("method")
        assert result is not None, "Required property 'method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path(self) -> builtins.str:
        '''(experimental) The path of this operation in the api.

        :stability: experimental
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def api(self) -> _aws_cdk_aws_apigateway_ceddda9d.SpecRestApi:
        '''(experimental) The api to grant permissions for.

        :stability: experimental
        '''
        result = self._values.get("api")
        assert result is not None, "Required property 'api' is missing"
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.SpecRestApi, result)

    @builtins.property
    def operation_id(self) -> builtins.str:
        '''(experimental) The ID of the operation for which permissions are being granted.

        :stability: experimental
        '''
        result = self._values.get("operation_id")
        assert result is not None, "Required property 'operation_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scope(self) -> _constructs_77d1e7e8.Construct:
        '''(experimental) The scope in which permission resources can be created.

        :stability: experimental
        '''
        result = self._values.get("scope")
        assert result is not None, "Required property 'scope' is missing"
        return typing.cast(_constructs_77d1e7e8.Construct, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IntegrationGrantProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.IntegrationRenderProps",
    jsii_struct_bases=[MethodAndPath],
    name_mapping={
        "method": "method",
        "path": "path",
        "operation_id": "operationId",
        "scope": "scope",
    },
)
class IntegrationRenderProps(MethodAndPath):
    def __init__(
        self,
        *,
        method: builtins.str,
        path: builtins.str,
        operation_id: builtins.str,
        scope: _constructs_77d1e7e8.Construct,
    ) -> None:
        '''(experimental) Properties for rendering an integration into an API Gateway OpenAPI extension.

        :param method: (experimental) The http method of this operation.
        :param path: (experimental) The path of this operation in the api.
        :param operation_id: (experimental) The ID of the operation being rendered.
        :param scope: (experimental) The scope in which the integration is being rendered.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e1ff24d14522d99e8359d6ebd416eaf7c94b70f565c15a4a5436fb2c13388a0)
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument operation_id", value=operation_id, expected_type=type_hints["operation_id"])
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "method": method,
            "path": path,
            "operation_id": operation_id,
            "scope": scope,
        }

    @builtins.property
    def method(self) -> builtins.str:
        '''(experimental) The http method of this operation.

        :stability: experimental
        '''
        result = self._values.get("method")
        assert result is not None, "Required property 'method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path(self) -> builtins.str:
        '''(experimental) The path of this operation in the api.

        :stability: experimental
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def operation_id(self) -> builtins.str:
        '''(experimental) The ID of the operation being rendered.

        :stability: experimental
        '''
        result = self._values.get("operation_id")
        assert result is not None, "Required property 'operation_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scope(self) -> _constructs_77d1e7e8.Construct:
        '''(experimental) The scope in which the integration is being rendered.

        :stability: experimental
        '''
        result = self._values.get("scope")
        assert result is not None, "Required property 'scope' is missing"
        return typing.cast(_constructs_77d1e7e8.Construct, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IntegrationRenderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/type-safe-api.SmithyBuildOptions",
    jsii_struct_bases=[SmithyCommon],
    name_mapping={
        "imports": "imports",
        "plugins": "plugins",
        "ignore_missing_plugins": "ignoreMissingPlugins",
        "maven": "maven",
        "projections": "projections",
    },
)
class SmithyBuildOptions(SmithyCommon):
    def __init__(
        self,
        *,
        imports: typing.Optional[typing.Sequence[builtins.str]] = None,
        plugins: typing.Optional[typing.Mapping[builtins.str, typing.Mapping[builtins.str, typing.Any]]] = None,
        ignore_missing_plugins: typing.Optional[builtins.bool] = None,
        maven: typing.Optional[typing.Union[SmithyMavenConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        projections: typing.Optional[typing.Mapping[builtins.str, typing.Union[SmithyProjection, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''(experimental) Options for the smithy build files.

        :param imports: (experimental) List of imports.
        :param plugins: (experimental) Plugins keyed by plugin id.
        :param ignore_missing_plugins: (experimental) If a plugin can't be found, Smithy will by default fail the build. This setting can be set to true to allow the build to progress even if a plugin can't be found on the classpath. Default: - no ignoreMissingPlugins set in the smithy-build.json file
        :param maven: (experimental) Maven configuration for the Smithy build project, used to specify dependencies and repositories in the build.gradle and smithy-build.json files. Default: the default configuration required for Smithy to OpenAPI conversion
        :param projections: (experimental) Map of projections name to projection configurations https://awslabs.github.io/smithy/2.0/guides/building-models/build-config.html#projections. Default: - no projections

        :stability: experimental
        '''
        if isinstance(maven, dict):
            maven = SmithyMavenConfiguration(**maven)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1477ffde6b8f14ddade40fb4a05df15f165cc5d439cce6b069f158b7e5e59aa7)
            check_type(argname="argument imports", value=imports, expected_type=type_hints["imports"])
            check_type(argname="argument plugins", value=plugins, expected_type=type_hints["plugins"])
            check_type(argname="argument ignore_missing_plugins", value=ignore_missing_plugins, expected_type=type_hints["ignore_missing_plugins"])
            check_type(argname="argument maven", value=maven, expected_type=type_hints["maven"])
            check_type(argname="argument projections", value=projections, expected_type=type_hints["projections"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if imports is not None:
            self._values["imports"] = imports
        if plugins is not None:
            self._values["plugins"] = plugins
        if ignore_missing_plugins is not None:
            self._values["ignore_missing_plugins"] = ignore_missing_plugins
        if maven is not None:
            self._values["maven"] = maven
        if projections is not None:
            self._values["projections"] = projections

    @builtins.property
    def imports(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of imports.

        :stability: experimental
        '''
        result = self._values.get("imports")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def plugins(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Mapping[builtins.str, typing.Any]]]:
        '''(experimental) Plugins keyed by plugin id.

        :stability: experimental
        '''
        result = self._values.get("plugins")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Mapping[builtins.str, typing.Any]]], result)

    @builtins.property
    def ignore_missing_plugins(self) -> typing.Optional[builtins.bool]:
        '''(experimental) If a plugin can't be found, Smithy will by default fail the build.

        This setting can be set to true to allow the build to progress
        even if a plugin can't be found on the classpath.

        :default: - no ignoreMissingPlugins set in the smithy-build.json file

        :stability: experimental
        '''
        result = self._values.get("ignore_missing_plugins")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def maven(self) -> typing.Optional[SmithyMavenConfiguration]:
        '''(experimental) Maven configuration for the Smithy build project, used to specify dependencies and repositories in the build.gradle and smithy-build.json files.

        :default: the default configuration required for Smithy to OpenAPI conversion

        :stability: experimental
        '''
        result = self._values.get("maven")
        return typing.cast(typing.Optional[SmithyMavenConfiguration], result)

    @builtins.property
    def projections(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, SmithyProjection]]:
        '''(experimental) Map of projections name to projection configurations https://awslabs.github.io/smithy/2.0/guides/building-models/build-config.html#projections.

        :default: - no projections

        :stability: experimental
        '''
        result = self._values.get("projections")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, SmithyProjection]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SmithyBuildOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApiGatewayIntegration",
    "ApiGatewayIntegrationResponse",
    "ApiGatewayIntegrationTlsConfig",
    "Authorizer",
    "AuthorizerProps",
    "Authorizers",
    "CidrAllowList",
    "CognitoAuthorizer",
    "CognitoAuthorizerProps",
    "CustomAuthorizer",
    "CustomAuthorizerProps",
    "CustomAuthorizerType",
    "DocumentationConfiguration",
    "DocumentationFormat",
    "GeneratedCodeOptions",
    "GeneratedCodeProjects",
    "GeneratedLibraryOptions",
    "GeneratedLibraryProjects",
    "IamAuthorizer",
    "InfrastructureConfiguration",
    "Integration",
    "IntegrationGrantProps",
    "IntegrationRenderProps",
    "Integrations",
    "LambdaIntegration",
    "Language",
    "Library",
    "LibraryConfiguration",
    "ManagedRule",
    "MethodAndPath",
    "ModelConfiguration",
    "ModelLanguage",
    "ModelOptions",
    "NoneAuthorizer",
    "OpenApiDefinition",
    "OpenApiDefinitionOptions",
    "OpenApiModelOptions",
    "RuntimeConfiguration",
    "SmithyBuildOptions",
    "SmithyCommon",
    "SmithyDefinition",
    "SmithyDefinitionOptions",
    "SmithyMavenConfiguration",
    "SmithyModelOptions",
    "SmithyProjection",
    "SmithyServiceName",
    "SmithyTransform",
    "TypeSafeApiIntegration",
    "TypeSafeApiModelProject",
    "TypeSafeApiModelProjectOptions",
    "TypeSafeApiOptions",
    "TypeSafeApiProject",
    "TypeSafeApiProjectOptions",
    "TypeSafeApiWebAclOptions",
    "TypeSafeRestApi",
    "TypeSafeRestApiProps",
]

publication.publish()

def _typecheckingstub__54bbaf1f62ed65563fa5fe86f006bb219a4165e70e8954489c0c8a57eb786208(
    *,
    cache_key_parameters: typing.Optional[typing.Sequence[builtins.str]] = None,
    cache_namespace: typing.Optional[builtins.str] = None,
    connection_id: typing.Optional[builtins.str] = None,
    connection_type: typing.Optional[builtins.str] = None,
    content_handling: typing.Optional[builtins.str] = None,
    credentials: typing.Optional[builtins.str] = None,
    http_method: typing.Optional[builtins.str] = None,
    passthrough_behavior: typing.Optional[builtins.str] = None,
    request_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    request_templates: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    responses: typing.Optional[typing.Mapping[builtins.str, typing.Union[ApiGatewayIntegrationResponse, typing.Dict[builtins.str, typing.Any]]]] = None,
    timeout_in_millis: typing.Optional[jsii.Number] = None,
    tls_config: typing.Optional[typing.Union[ApiGatewayIntegrationTlsConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    type: typing.Optional[builtins.str] = None,
    uri: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac85c5045c3a1b7e5fa301a20c8e42758a5987c59645f4aa7d181d4e3c67f689(
    *,
    response_parameters: typing.Mapping[builtins.str, builtins.str],
    response_templates: typing.Mapping[builtins.str, builtins.str],
    status_code: builtins.str,
    content_handling: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13da332b7a7dcdfb32928a99f0c6dc04a61d0d2e03fed3b12937ae3d342aea5b(
    *,
    insecure_skip_verification: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a0b3bb1dc7df594503f85f7e4e203386d8288de3b7e59c33559a1bce31752f5(
    *,
    authorization_type: _aws_cdk_aws_apigateway_ceddda9d.AuthorizationType,
    authorizer_id: builtins.str,
    authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97fa5bbc32d6acfd09f204cad081dd902df873b5c29715c0f84e02901c4e9832(
    *,
    cidr_ranges: typing.Sequence[builtins.str],
    cidr_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51ad75e89d4fbd5ec94d8c79816220551ccdb66a806955f5c168569c64b87077(
    *authorization_scopes: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62ee5045c6a49973b02f825688c3321a300b9100cdd48a84a93dbe932ffac51a(
    *,
    authorizer_id: builtins.str,
    user_pools: typing.Sequence[_aws_cdk_aws_cognito_ceddda9d.IUserPool],
    authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c71002e919737a01a6f2695f649dec4346581e930ea1d02961439b5ea0b0fe9(
    *,
    authorizer_id: builtins.str,
    function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    authorizer_result_ttl_in_seconds: typing.Optional[jsii.Number] = None,
    identity_source: typing.Optional[builtins.str] = None,
    type: typing.Optional[CustomAuthorizerType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0fd7650b3ad306974000ccd92a709cb54595a5ac502052bb19f206b5ad36d3e(
    *,
    formats: typing.Sequence[DocumentationFormat],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23f41be8cb8518404a72409561f18dfc9dcf036ff46fc15a66438b4aad08e69c(
    *,
    java: typing.Optional[typing.Union[_projen_java_04054675.JavaProjectOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    python: typing.Optional[typing.Union[_projen_python_04054675.PythonProjectOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    typescript: typing.Optional[typing.Union[_projen_typescript_04054675.TypeScriptProjectOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0f400533db43e5c38defa1fec15b1bd673fa5a195759697379ba33d179a60b5(
    *,
    java: typing.Optional[_projen_java_04054675.JavaProject] = None,
    python: typing.Optional[_projen_python_04054675.PythonProject] = None,
    typescript: typing.Optional[_projen_typescript_04054675.TypeScriptProject] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aaba6490bdd657ac25f54e9f2eaacb24cb65c191d4ec347ee3547a98abae3956(
    *,
    typescript_react_query_hooks: typing.Optional[typing.Union[_projen_typescript_04054675.TypeScriptProjectOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31ee7e756a53a88db35aef6ee5d346bfd3c90aab725573d11722d24b6973ea0e(
    *,
    typescript_react_query_hooks: typing.Optional[_projen_typescript_04054675.TypeScriptProject] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42832742ccb56b4504cad0e669390b735f9f726fc938f2b7eb2d7878b53e3faf(
    *,
    language: Language,
    options: typing.Optional[typing.Union[GeneratedCodeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e282d4562d6f4a6d2012128cec34ed04419998a73c33d70b6d7ac593f6da8f5(
    lambda_function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4f33cbf9ca3cf26ca56b9477805b0ee2228ee2f97e63a0addace46ae5267b4d(
    lambda_function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf885e298875e06aa5677eb9355657441701a5f252c8eca8317f989a12fb7d82(
    *,
    libraries: typing.Sequence[Library],
    options: typing.Optional[typing.Union[GeneratedLibraryOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5526168b6baf723196f879ba4ca6bcce6f57e83cf0e96d3c912a0ab422a07e3(
    *,
    name: builtins.str,
    vendor: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__002fb094dfb3c5bb8ab5a5455ef75fa49e10214af4f996e8ec7c98bfb10fe67a(
    *,
    method: builtins.str,
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86eb139bc129f96c7fb27199a03837046b0d025d1e87b5911e8cf218d7f4eae6(
    *,
    language: ModelLanguage,
    options: typing.Union[ModelOptions, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19b2eb4034a9eda1968994c2e7da74dca6c331bf42f0c1dc88c09da184b11ef4(
    *,
    openapi: typing.Optional[typing.Union[OpenApiModelOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    smithy: typing.Optional[typing.Union[SmithyModelOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__370ebffac0840359674dee761aaeaa906d40299ef3ec2d6323f2214155e1db2d(
    project: TypeSafeApiModelProject,
    *,
    open_api_options: typing.Union[OpenApiModelOptions, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__591f8c9caef1c0f0144c3c8f46e6c9515a9b59283a269f9a55ff68f0655c28bd(
    *,
    open_api_options: typing.Union[OpenApiModelOptions, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4384c14a609de971de6d097c833aea11812d657157670113cb85f7eeca095985(
    *,
    title: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3be12f3081726e44a0f5ea07c36e418c48204b3fee82192c24e1eb2cb72d1f10(
    *,
    languages: typing.Sequence[Language],
    options: typing.Optional[typing.Union[GeneratedCodeOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eef1a858c59c498786d12a5a49debb2c3a22b53c0435a8b44fac4d42f40f4c70(
    *,
    imports: typing.Optional[typing.Sequence[builtins.str]] = None,
    plugins: typing.Optional[typing.Mapping[builtins.str, typing.Mapping[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da45c4bac118e04412e8a56eb9f701f415202aec168d3c649824a65a789cbdbd(
    project: TypeSafeApiModelProject,
    *,
    smithy_options: typing.Union[SmithyModelOptions, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__671cc8c9571996d8a6bd6cffe56aa2f3c23025d1e0f1b630b4a312786ae8d84a(
    *deps: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b4739ed02d1dd3269fca1e6cf1c9dda195085fbcf4af8a48df5573dbe28ee82(
    *deps: SmithyDefinition,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__036ba6d3e9b28066c60f4c0d3d8829c325d7b35770e1fe8c5d663bd4c2a2ce63(
    *,
    smithy_options: typing.Union[SmithyModelOptions, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0658a2f7e63bc2e040803cf6247a71762da6c3f26d27fc3438d10efa0c2b0014(
    *,
    dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
    repository_urls: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1182563a4207fde8baf185b6ac26b24239cff2142fe1cf342b86e5c28d28f024(
    *,
    service_name: typing.Union[SmithyServiceName, typing.Dict[builtins.str, typing.Any]],
    ignore_gradle_wrapper: typing.Optional[builtins.bool] = None,
    ignore_smithy_build_output: typing.Optional[builtins.bool] = None,
    smithy_build_options: typing.Optional[typing.Union[SmithyBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c5ea0995b3408d3ccc8ee5fc34a1f8f7663272a167626570de8efcb270b989c(
    *,
    imports: typing.Optional[typing.Sequence[builtins.str]] = None,
    plugins: typing.Optional[typing.Mapping[builtins.str, typing.Mapping[builtins.str, typing.Any]]] = None,
    abstract: typing.Optional[builtins.bool] = None,
    transforms: typing.Optional[typing.Sequence[typing.Union[SmithyTransform, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33167c5a545168279a3c6fd39d00c6b82f7fe43cb1586a4257803dd35a4a0365(
    *,
    namespace: builtins.str,
    service_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4424e16fdd9894bdf9f73356687f8b13ded16ea8986897f93021567a26e01262(
    *,
    args: typing.Mapping[builtins.str, typing.Any],
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6aac208a4d52a45aa5a05fdd9df9236f624116cf700032ca2ec93451ea1ee14c(
    *,
    integration: Integration,
    authorizer: typing.Optional[Authorizer] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab9fbe8ba5379dfe513c8876edcc903cdd8e15a6de4c21aa838dc6c6c7b2402a(
    *,
    name: builtins.str,
    commit_generated: typing.Optional[builtins.bool] = None,
    git_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    git_options: typing.Optional[typing.Union[_projen_04054675.GitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    logging: typing.Optional[typing.Union[_projen_04054675.LoggerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    outdir: typing.Optional[builtins.str] = None,
    parent: typing.Optional[_projen_04054675.Project] = None,
    projen_command: typing.Optional[builtins.str] = None,
    projenrc_json: typing.Optional[builtins.bool] = None,
    projenrc_json_options: typing.Optional[typing.Union[_projen_04054675.ProjenrcJsonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    renovatebot: typing.Optional[builtins.bool] = None,
    renovatebot_options: typing.Optional[typing.Union[_projen_04054675.RenovatebotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    model_language: ModelLanguage,
    model_options: typing.Union[ModelOptions, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddffe68493ea33b13b142dd3a74d4b71e0e9eb563dc8d340916de145a0d0dfd3(
    *,
    integrations: typing.Mapping[builtins.str, typing.Union[TypeSafeApiIntegration, typing.Dict[builtins.str, typing.Any]]],
    operation_lookup: typing.Mapping[builtins.str, typing.Union[MethodAndPath, typing.Dict[builtins.str, typing.Any]]],
    cors_options: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.CorsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    default_authorizer: typing.Optional[Authorizer] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abde6fa90ff9fea9e430aaca82f0c910c5ecc24d1205ba19958f47080d5b15fb(
    *,
    name: builtins.str,
    commit_generated: typing.Optional[builtins.bool] = None,
    git_ignore_options: typing.Optional[typing.Union[_projen_04054675.IgnoreFileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    git_options: typing.Optional[typing.Union[_projen_04054675.GitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    logging: typing.Optional[typing.Union[_projen_04054675.LoggerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    outdir: typing.Optional[builtins.str] = None,
    parent: typing.Optional[_projen_04054675.Project] = None,
    projen_command: typing.Optional[builtins.str] = None,
    projenrc_json: typing.Optional[builtins.bool] = None,
    projenrc_json_options: typing.Optional[typing.Union[_projen_04054675.ProjenrcJsonOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    renovatebot: typing.Optional[builtins.bool] = None,
    renovatebot_options: typing.Optional[typing.Union[_projen_04054675.RenovatebotOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    infrastructure: typing.Union[InfrastructureConfiguration, typing.Dict[builtins.str, typing.Any]],
    model: typing.Union[ModelConfiguration, typing.Dict[builtins.str, typing.Any]],
    runtime: typing.Union[RuntimeConfiguration, typing.Dict[builtins.str, typing.Any]],
    documentation: typing.Optional[typing.Union[DocumentationConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    library: typing.Optional[typing.Union[LibraryConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__767125a1376366edf6341c113fbc39f6e469b47eea26e1fa3720cfc786f2d558(
    *,
    cidr_allow_list: typing.Optional[typing.Union[CidrAllowList, typing.Dict[builtins.str, typing.Any]]] = None,
    disable: typing.Optional[builtins.bool] = None,
    managed_rules: typing.Optional[typing.Sequence[typing.Union[ManagedRule, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e4821d6581d103cd1939ca5166c26d862d1742c080c74994a7cd4722c1c2d19(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    spec_path: builtins.str,
    web_acl_options: typing.Optional[typing.Union[TypeSafeApiWebAclOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    cloud_watch_role: typing.Optional[builtins.bool] = None,
    deploy: typing.Optional[builtins.bool] = None,
    deploy_options: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.StageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    disable_execute_api_endpoint: typing.Optional[builtins.bool] = None,
    domain_name: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.DomainNameOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    endpoint_export_name: typing.Optional[builtins.str] = None,
    endpoint_types: typing.Optional[typing.Sequence[_aws_cdk_aws_apigateway_ceddda9d.EndpointType]] = None,
    fail_on_warnings: typing.Optional[builtins.bool] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
    rest_api_name: typing.Optional[builtins.str] = None,
    retain_deployments: typing.Optional[builtins.bool] = None,
    integrations: typing.Mapping[builtins.str, typing.Union[TypeSafeApiIntegration, typing.Dict[builtins.str, typing.Any]]],
    operation_lookup: typing.Mapping[builtins.str, typing.Union[MethodAndPath, typing.Dict[builtins.str, typing.Any]]],
    cors_options: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.CorsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    default_authorizer: typing.Optional[Authorizer] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6abf7110490d9869d975a50b9fe29f98259a9a230be2bbcde1c8e0ea1fd15771(
    *,
    cloud_watch_role: typing.Optional[builtins.bool] = None,
    deploy: typing.Optional[builtins.bool] = None,
    deploy_options: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.StageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    disable_execute_api_endpoint: typing.Optional[builtins.bool] = None,
    domain_name: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.DomainNameOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    endpoint_export_name: typing.Optional[builtins.str] = None,
    endpoint_types: typing.Optional[typing.Sequence[_aws_cdk_aws_apigateway_ceddda9d.EndpointType]] = None,
    fail_on_warnings: typing.Optional[builtins.bool] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
    rest_api_name: typing.Optional[builtins.str] = None,
    retain_deployments: typing.Optional[builtins.bool] = None,
    integrations: typing.Mapping[builtins.str, typing.Union[TypeSafeApiIntegration, typing.Dict[builtins.str, typing.Any]]],
    operation_lookup: typing.Mapping[builtins.str, typing.Union[MethodAndPath, typing.Dict[builtins.str, typing.Any]]],
    cors_options: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.CorsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    default_authorizer: typing.Optional[Authorizer] = None,
    spec_path: builtins.str,
    web_acl_options: typing.Optional[typing.Union[TypeSafeApiWebAclOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a68568c451e2693b26c89a6bdf98c3e1d54546a0033bfd04bfa581e39ee47c28(
    *,
    method: builtins.str,
    path: builtins.str,
    api: _aws_cdk_aws_apigateway_ceddda9d.SpecRestApi,
    operation_id: builtins.str,
    scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e1ff24d14522d99e8359d6ebd416eaf7c94b70f565c15a4a5436fb2c13388a0(
    *,
    method: builtins.str,
    path: builtins.str,
    operation_id: builtins.str,
    scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1477ffde6b8f14ddade40fb4a05df15f165cc5d439cce6b069f158b7e5e59aa7(
    *,
    imports: typing.Optional[typing.Sequence[builtins.str]] = None,
    plugins: typing.Optional[typing.Mapping[builtins.str, typing.Mapping[builtins.str, typing.Any]]] = None,
    ignore_missing_plugins: typing.Optional[builtins.bool] = None,
    maven: typing.Optional[typing.Union[SmithyMavenConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    projections: typing.Optional[typing.Mapping[builtins.str, typing.Union[SmithyProjection, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass
