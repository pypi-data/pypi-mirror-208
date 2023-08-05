## Overview

An open source Python CLI tool which runs locally and will automatically claim rewards for all your created offers on [dexie](https://dexie.space).

## Installing

### Install via pip

```sh
pip install dexie-rewards
```

### Install via the repository

1. Clone the repository

```sh
git clone git@github.com:dexie-space/dexie-rewards.git
cd ./dexie-rewards/
```

2. Activate Poetry Shell

```sh
❯ poetry shell
Spawning shell within ...

❯ emulate bash -c '.../bin/activate'
```

3. Install Dexie CLI

```sh
❯ poetry install
Installing dependencies from lock file

Package operations: 54 installs, 1 update, 0 removals

  ...
  • Installing chia-blockchain (...)
  • Installing rich-click (...)

Installing the current project: dexie-rewards (...)
```

### Set `CHIA_ROOT` and dexie urls (optional)

> Dexie CLI needs to know where to connect to the dexie-api and where to find the chia wallet.

```sh
❯ export CHIA_ROOT="~/.chia/testnet10"
❯ export DEXIE_URL="https://testnet.dexie.space"
❯ export DEXIE_API_URL="https://api-testnet.dexie.space/v1/"
```

## Commands

```sh
❯ dexie --help

 Usage: dexie [OPTIONS] COMMAND [ARGS]...

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────╮
│ --version      Show the version and exit.                                                     │
│ --help         Show this message and exit.                                                    │
╰───────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────────╮
│ rewards           Manage your dexie rewards for offers                                        │
╰───────────────────────────────────────────────────────────────────────────────────────────────╯
```

### Rewards

```sh
❯ dexie rewards --help

 Usage: dexie rewards [OPTIONS] COMMAND [ARGS]...

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────╮
│ --help      Show this message and exit.                                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────────╮
│ claim          Claim all offers with dexie rewards                                            │
│ list           List all offers with dexie rewards                                             │
╰───────────────────────────────────────────────────────────────────────────────────────────────╯
```

#### list

```sh
❯ dexie rewards list --help

 Usage: dexie rewards list [OPTIONS]

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────╮
│ --fingerprint  -f  INTEGER  Set the fingerprint to specify which wallet to use                │
│ --json         -j           Displays offers as JSON                                           │
│ --help                      Show this message and exit.                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────╯

❯ dexie rewards list
Using wallet with fingerprint: 518185849
╭──────────────────────────────────────────────┬───────────────╮
│                    Offer                     │ Rewards (DBX) │
├──────────────────────────────────────────────┼───────────────┤
│ CWkZDUURQioPtKjF2zWUHqf6vxEQDhjEnCk6TJqoTpPe │         0.864 │
│ J12qwA7fAC2jFm7AjNB2H7DKRzZ2ajfbMBygnRrhjrVM │         0.126 │
│ 5gkKdAg93TbnUSSJLbhCEhWw9zHXWMxggWQmshQiKUuP │         0.805 │
├──────────────────────────────────────────────┼───────────────┤
│      Found 3 offers with total rewards       │         1.795 │
╰──────────────────────────────────────────────┴───────────────╯

❯ dexie rewards list -f 518185849 --json | jq
[
  {
    "id": "CWkZDUURQioPtKjF2zWUHqf6vxEQDhjEnCk6TJqoTpPe",
    "status": 0,
    "date_found": "2023-05-08T13:31:49.033Z",
    "date_rewards_since": "2023-05-08T13:32:24.623Z",
    "maker_puzzle_hash": "0xe762f668c631ec2bd6f909cfdfc42d56a281e5e5be03bd8a021900ecb6917d78",
    "claimable_rewards": 0.864
  },
  {
    "id": "J12qwA7fAC2jFm7AjNB2H7DKRzZ2ajfbMBygnRrhjrVM",
    "status": 4,
    "date_found": "2023-05-08T10:26:28.083Z",
    "date_rewards_since": "2023-05-08T10:33:05.237Z",
    "maker_puzzle_hash": "0xe762f668c631ec2bd6f909cfdfc42d56a281e5e5be03bd8a021900ecb6917d78",
    "claimable_rewards": 0.126
  },
  {
    "id": "5gkKdAg93TbnUSSJLbhCEhWw9zHXWMxggWQmshQiKUuP",
    "status": 4,
    "date_found": "2023-05-08T10:24:42.258Z",
    "date_rewards_since": "2023-05-08T10:25:05.167Z",
    "maker_puzzle_hash": "0xe762f668c631ec2bd6f909cfdfc42d56a281e5e5be03bd8a021900ecb6917d78",
    "claimable_rewards": 0.805
  }
]
```

#### claim

```sh
❯ dexie rewards claim --help

 Usage: dexie rewards claim [OPTIONS]

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────╮
│ --fingerprint  -f   INTEGER  Set the fingerprint to specify which wallet to use               │
│ --verify-only  -vo           Only verify the claim, don't actually claim                      │
│ --yes          -y            Skip claim confirmation                                          │
│ --verbose      -v            Display verbose output                                           │
│ --help                       Show this message and exit.                                      │
╰───────────────────────────────────────────────────────────────────────────────────────────────╯

❯ dexie rewards claim -f 518185849 --verbose
╭──────────────────────────────────────────────┬───────────────╮
│                    Offer                     │ Rewards (DBX) │
├──────────────────────────────────────────────┼───────────────┤
│ CWkZDUURQioPtKjF2zWUHqf6vxEQDhjEnCk6TJqoTpPe │         0.864 │
│ J12qwA7fAC2jFm7AjNB2H7DKRzZ2ajfbMBygnRrhjrVM │         0.126 │
│ 5gkKdAg93TbnUSSJLbhCEhWw9zHXWMxggWQmshQiKUuP │         0.805 │
├──────────────────────────────────────────────┼───────────────┤
│      Found 3 offers with total rewards       │         1.795 │
╰──────────────────────────────────────────────┴───────────────╯
Claim all? [y/n]: y

claims request payload:
{
  "claims": [
    {
      "offer_id": "CWkZDUURQioPtKjF2zWUHqf6vxEQDhjEnCk6TJqoTpPe",
      "signature": "8c46a42998ad7089a50d3b92bb194a4d3ded1d3f9ae7911949ae561e48076d05eb11817e65984dec9c746d9bb17da1c714c0138a7fa36a057388e5df247d3309723ec28e3e0b84bde6f927f1ead77e5bdae0ecf855ffd838798ef74dc06f1d46",
      "public_key": "b3406aa1620c09fa9c653019c1f071c330a69829d3adfd4eb735e4518ca9717e9f47e66902e06fa9beb9d3d026acb042"
    },
    {
      "offer_id": "J12qwA7fAC2jFm7AjNB2H7DKRzZ2ajfbMBygnRrhjrVM",
      "signature": "abf567d26a5332461daf404c6482c9214b5f6955b87cffaad1290a96d7bb0184317e8963a5b44a19ca9b159a6c80137502bf2f83531adec8b1a5d22b118624b3ba06a676f0f2fa05d3cd533eb3d74c097b6cf9cd4e4d515fa1160b6dc565e817",
      "public_key": "b3406aa1620c09fa9c653019c1f071c330a69829d3adfd4eb735e4518ca9717e9f47e66902e06fa9beb9d3d026acb042"
    },
    {
      "offer_id": "5gkKdAg93TbnUSSJLbhCEhWw9zHXWMxggWQmshQiKUuP",
      "signature": "a17eedb2d8f0ad31c1ad93de4a288bcb85241c952d2b0fb2d1d583aec6d1f8b858858055c4893a3b6d23283e590dc9a302fac5e434e5e0800337c872f3efd50542f1140298e8e4e29e80b1100d164f33248a38d2efbe53f124d3772205160d72",
      "public_key": "b3406aa1620c09fa9c653019c1f071c330a69829d3adfd4eb735e4518ca9717e9f47e66902e06fa9beb9d3d026acb042"
    }
  ]
}

claims result:
{
  "success": true,
  "verified_amount": {
    "CWkZDUURQioPtKjF2zWUHqf6vxEQDhjEnCk6TJqoTpPe": 0.864,
    "J12qwA7fAC2jFm7AjNB2H7DKRzZ2ajfbMBygnRrhjrVM": 0.126,
    "5gkKdAg93TbnUSSJLbhCEhWw9zHXWMxggWQmshQiKUuP": 0.805
  }
}


```
