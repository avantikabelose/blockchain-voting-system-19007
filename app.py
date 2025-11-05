from flask import Flask, request, render_template_string
import hashlib
import json
from datetime import datetime, timezone

app = Flask(__name__)

# -------------------------
# Blockchain Class
# -------------------------
class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_votes = []
        # Create the Genesis Block
        self.create_block(proof=100, previous_hash='1')

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'votes': self.current_votes.copy(),
            'proof': proof,
            'previous_hash': previous_hash
        }
        self.current_votes = []
        self.chain.append(block)
        return block

    def add_vote(self, voter_id, voter_name, candidate):
        self.current_votes.append({
            'voter_id': voter_id,
            'voter_name': voter_name,
            'candidate_voted': candidate
        })
        return self.last_block['index'] + 1 if self.chain else 1

    @staticmethod
    def hash(block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1] if self.chain else None

    def proof_of_work(self, last_proof):
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f"{last_proof}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


# -------------------------
# Initialize Blockchain
# -------------------------
blockchain = Blockchain()

# -------------------------
# HTML Template
# -------------------------
template = '''
<!DOCTYPE html>
<html>
<head>
    <title>🗳 Blockchain-Based Voting System</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f4f6f8;
            margin: 40px;
        }
        h1, h2 { color: #222; }
        form {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 3px 8px rgba(0,0,0,0.1);
            max-width: 500px;
            margin-bottom: 40px;
        }
        input, select, button {
            padding: 10px;
            margin: 8px 0;
            width: 100%;
            box-sizing: border-box;
            font-size: 15px;
        }
        button {
            background: #2E8B57;
            color: white;
            border: none;
            cursor: pointer;
            border-radius: 5px;
        }
        button:hover { background: #1F5E3C; }
        .block {
            background: white;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 5px solid #2E8B57;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            max-width: 900px;
            border-radius: 6px;
        }
        pre {
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .footer {
            margin-top: 50px;
            color: gray;
            font-size: 14px;
        }
    </style>
</head>
<body>

    <h1>🗳 Blockchain-Based Voting System</h1>
    <p>This decentralized system records votes securely on a blockchain ledger to ensure transparency and immutability.</p>

    <form action="/add_vote" method="post">
        <input type="text" name="voter_id" placeholder="Voter ID" required>
        <input type="text" name="voter_name" placeholder="Voter Name" required>
        <select name="candidate" required>
            <option value="">-- Select Candidate --</option>
            <option value="Candidate A">Candidate A</option>
            <option value="Candidate B">Candidate B</option>
            <option value="Candidate C">Candidate C</option>
        </select>
        <button type="submit">Cast Vote</button>
    </form>

    <h2>📜 Blockchain Ledger (Voting Records)</h2>
    {% for block in chain %}
        <div class="block">
            <pre>{{ block | tojson(indent=2) }}</pre>
        </div>
    {% endfor %}

    <div class="footer">
        <p>© 2025 Blockchain Voting System | Ensuring Fair & Transparent Elections</p>
    </div>

</body>
</html>
'''

# -------------------------
# Flask Routes
# -------------------------
@app.route('/')
def index():
    return render_template_string(template, chain=blockchain.chain)

@app.route('/add_vote', methods=['POST'])
def add_vote():
    voter_id = request.form['voter_id']
    voter_name = request.form['voter_name']
    candidate = request.form['candidate']

    blockchain.add_vote(voter_id, voter_name, candidate)

    last_proof = blockchain.last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    previous_hash = blockchain.hash(blockchain.last_block)
    blockchain.create_block(proof, previous_hash)

    return render_template_string(template, chain=blockchain.chain)

# -------------------------
# Run the App
# -------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
