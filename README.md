# Kudu

A limited implementation of [Vuvuzela](https://vuvuzela.io/) for [ECS153](https://bob.cs.ucdavis.edu/classes/s19-ecs153/index.html).

![Kudu scene from Natural History Museums of Los Angeles County](https://nhm.org/site/sites/default/files/exhibits/halls/african/amh_kudu.jpg)

See [here](https://dl.acm.org/citation.cfm?id=2815417) or the `references` directory for details.

## Installation

See Flask [docs](http://flask.pocoo.org/docs/1.0/installation/) for setup info.

Run `pip install -r requirements.txt` to install dependencies.

The use of a [virtual environment](https://docs.python.org/3/library/venv.html) and Python 3.7 or later is recommended.

## Use

Kudu requires the launching two separate server processes and a number of clients.

### Minimal Demonstration

For two (`2`) clients.

Run each executable in a shell using the virtual environment.

Launch the dispatch server to facilitate key-exchanges:

```
python3 dispatch/dispatch.py 2
```

Launch the Kudu server to that handles the message processing:

```
python3 server/app.py 2
```

Launch a pair of clients to be conversation partners.

Identifier: 'foo'

```
python3 client/client.py foo bar
```

Identifier: 'bar'

```
python3 client/client.py bar foo
```

Each clients should prompt for a message to send to its partner.

See the help text of each executable for additional information.

#### Linux

The `./launcher.py` script allows a similar demonstration to be easily be spun up.

## Implementation Details

A note on terminology:

* Vuvuzela is the referenced research paper.

* Kudu is our limited implementation designed to illustrate some of the more interesting and unique aspects of Vuvuzela.

Assuming familiarity with the Vuvuzela paper, a concise summary of this implementation.

In several areas, Kudu deviates from the source reference; these design choices were generally simplifications as we prioritized the more interesting elements of Vuvuzela.

In the barest terms, our implementation, Kudu, is a simplification of the middle-portion: No clients are joining nor leaving, and each client has one and exactly partner unique to it to converse with for the full duration of its lifespan.

### Significant Variances

#### Preface

Note that, taken together, the timing and inactive participant simplifications to Kudu maintain the guarantee that a strong (full network observation plus all but one server) adversary gains no knowledge of conversation partners, as in the full Vuvuzela.

That is to say, the strong adversary knows a user is connected to Kudu but gains no additional knowledge regarding the user's conversation partner nor their activity level (i.e. actively sending authentic messages vs passively sending noise placeholders).

#### Timing

The client and servers lack an implemented timing element: The server waits until each registered client sends its messages and collects the response rather than mode-switching based on a timer (as in the full Vuvuzela).

The Kudu client is able to send noise messages to its partner and recognize the same on receipt; we require the user to actively confirm the noisy-no-message rather than operating a timeout.

This implementation accurately replicates Vuvuzela's critical behavior that each client sends and collects exactly one message per round to protect against statistical analysis of participation.

The limitation of this server-wait simplification is that it requires each and every client to be connected and actively participate: It will hang until all clients have participated during the round.

The benefit is bypassing troublesome concurrency and synchronization issues.

As the Vuvuzela guarantees are predicated on a client's constant connection (and consequent noise generation) to the network, we find this to be a reasonable assumption. 

This does choice does not affect Vuvuzela's guarantees of anonymity.

#### Non-conversant (inactive) clients

The Kudu implementation assumes each client has a (fixed) partner.

This is obviously a limitation but doing so bypassed some uninteresting implementation detail.

#### Server Chain

Kudu uses a single process to simulate the server-chain. This simplification avoids the implementation details of an inter-server API.

Kudu maintains the isolation of data between simulated servers (each referred to as a `Bundle`): The implementation effectively showcases the mix-net and its applications in isolating client from message.

### Unimplemented Features

#### Inter-server noise generation

The result of this omission is a partial loss of the Vuvuzela's guarantees against a strong adversary: Namely an adversary capable of *manipulation* of (i.e. dropping) network traffic to isolate two users as a rounds exclusive participants and check for a shared deaddrop.

The guarantee of anonymity against a (weaker) strong adversary able limited to observation is maintained by the mix-net.
