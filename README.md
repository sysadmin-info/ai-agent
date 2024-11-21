# ai-agent
AI agent rewritten from TypeScript into Python

Original source: [aidevs agent cracker](https://github.com/iceener/aidevs-agent-cracker)

Clone the repository:

```bash
git clone https://github.com/sysadmin-info/ai-agent.git
```

Install Ansible using the below tutorial:

[step-by-step AI agent development with Python and Ansible](https://sysadmin.info.pl/en/blog/step-by-step-ai-agent-development-with-python-and-ansible/)

Run the playbook:

```bash
ansible-playbook site.yml
```

Switch the virtual environment for Python:

```bash  
python3 -m venv venv  
source venv/bin/activate  # Linux/macOS  
```  

Or add to `.bashrc` this:

```bash
alias activate-aidevs="source $HOME/aidevs/agent/venv/bin/activate"
```

And then execute this:

```bash
source ~/.bashrc
```

Run the endpoint:

```bash
uvicorn index:app --host 0.0.0.0 --port 3000
```

In second terminal/tty run curl

```bash
curl -X POST http://localhost:3000 -H "Content-Type: application/json" -d '{"messages": [{"role": "user", "content": "How far is the Moon?"}]}'
```
