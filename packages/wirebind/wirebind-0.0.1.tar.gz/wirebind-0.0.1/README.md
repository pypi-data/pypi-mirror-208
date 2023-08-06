# wirebind

[![Python Tests](https://github.com/drifting-in-space/wirebind/actions/workflows/python.yml/badge.svg)](https://github.com/drifting-in-space/wirebind/actions/workflows/python.yml)

In a typical client/server application, the client and server communicate by passing messages to each other. Wirebind allows applications to instead interact with local data structures, which it synchronizes over a long-lived WebSocket connection.

The goal of wirebind is to make client/server applications as fun to build as single-process ones.
