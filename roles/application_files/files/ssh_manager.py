# ssh_manager.py
import asyncssh
import asyncio

class AsyncSSHManager:
    def __init__(self, hostname: str, username: str, password: str):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.connection = None

    async def connect(self):
        """Establish an SSH connection."""
        self.connection = await asyncssh.connect(
            self.hostname,
            username=self.username,
            password=self.password
        )

    async def execute_command(self, command: str) -> str:
        """Execute a command over SSH and return the output."""
        if self.connection is None:
            raise ValueError("No active SSH connection")
        result = await self.connection.run(command, check=True)
        return result.stdout

    async def close_connection(self):
        """Close the SSH connection."""
        if self.connection:
            self.connection.close()
            await self.connection.wait_closed()
            self.connection = None
