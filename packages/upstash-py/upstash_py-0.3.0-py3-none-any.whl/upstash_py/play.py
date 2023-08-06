from upstash_py.client import Redis
from upstash_py.http.decode import decode
from asyncio import get_event_loop


redis = Redis(
    url="https://funky-grubworm-30552.upstash.io",
    token="AXdYASQgNmVmN2RhOTQtMmM4OS00ZDEyLThhNzYtNDdmYjQyNGZlODRiOTZlYTgzZjJiODc4NDAwMzlhN2UyMzk5YTcwYzEzZGE=",
)


async def main():
    """
    async with redis:
        assert await redis.georadius(
            "test_geo_index",
            longitude=15,
            latitude=37,
            radius=200,
            unit="KM",
            with_coordinates=True
        ) == [
            {"member": "Palermo", "longitude": 13.361389338970184, "latitude": 38.115556395496299},
            {"member": "Catania", "longitude": 15.087267458438873, "latitude": 37.50266842333162}
        ]
    """
    raw = [
        ['Palermo', ['MTMuMzYxMzg5MzM4OTcwMTg0', 'MzguMTE1NTU2Mzk1NDk2Mjk5']],
        ['Catania', ['MTUuMDg3MjY3NDU4NDM4ODcz', 'MzcuNTAyNjY4NDIzMzMxNjI=']]
    ]
    print(decode())

loop = get_event_loop()
loop.run_until_complete(main())
