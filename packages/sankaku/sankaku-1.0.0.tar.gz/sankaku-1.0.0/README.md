<h1 align="center">
  <a>
    <img src="https://beta.sankakucomplex.com/images/apple-touch-icon.png" 
    width="150" height="150">
  </a>
  <div>sankaku</div>
</h1>
<p align="center"><em><b>For real men of culture </b></em>&#128527</p>

## About

Asynchronous API wrapper for [Sankaku Complex](https://beta.sankakucomplex.com)
with *type-hinting*, pydantic *data validation* and an optional *logging support*
with loguru.

### Features:

- Type-hints
- Deserialization of raw json data thanks to pydantic models
- Enumerations for API request parameters to provide better user experience
  > For instance, you can type `types.TagType.ARTIST` instead of `types[]=1`

---

Documentation: TBA

Source code: https://github.com/zerex290/sankaku

---

## Requirements

- Python 3.11+
- aiohttp
- pydantic
- loguru

## Installation

```commandline
pip install sankaku
```

## Example

It's very simple to use and doesn't require to always keep opened browser page
with documentation because all methods are self-explanatory.

```py
import asyncio
from sankaku import SankakuClient

async def main():
    client = SankakuClient()

    post = await client.get_post(25742064)
    print(f"Rating: {post.rating} | Created: {post.created_at}")
    # "Rating: Rating.QUESTIONABLE | Created: 2021-08-01 23:18:52+03:00"

    await client.login(access_token="token")
    # Or you can authorize by credentials:
    # await client.login(login="nickname or email", password="password")
    async for book in client.get_recently_read_books():
        ...

asyncio.run(main())
```
