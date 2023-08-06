Ever wanted to stream large JSON objects with [`FastAPI`](https://fastapi.tiangolo.com/) asynchrounously?
Look no more, `iteriotools` is the solution you've been looking for!

It provides a `RawIterIO` class which can wrap an iterator of bytes into a read-only file-like object.

# Example

```bash
cd example
```

To run the example project's application:

```bash
pipenv run uvicorn --reload project:app
```

To demonstrate the impact of `RawIterIO` on streaming large JSON objects, first emulate a "liveness probe" by running
the following:

```bash
while time curl --silent http://127.0.0.1:8000/health > /dev/null; do :; done
```

Then, while still having the probe running, emulate a few clients `GET`-ing some large JSON object with:

```bash
(
    trap -- 'kill 0' EXIT
    for _ in {0..31}; do
        while curl --silent http://127.0.0.1:8000/users/batched > /dev/null; do :; done &
    done
    wait
)
```

You should notice a significant increase in response time on the "liveness probe" (e.g. 0.003 seconds --> 25 seconds).

Now, with the version that utilizes `RawIterIO` to stream JSON chunk by chunk:

```bash
(
    trap -- 'kill 0' EXIT
    for _ in {0..31}; do
        while curl --silent http://127.0.0.1:8000/users/streamed > /dev/null; do :; done &
    done
    wait
)
```

You should still notice a significant increase in response time, but way less extreme (e.g. 0.003 seconds -> 2
seconds), and that numbers scales better with the size of the JSON object being streamed instead of being batched.
