import json
import hashlib
import time

class Block:
    def __init__(self, index, timestamp, data, previous_hash, version_changes):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.version_changes = version_changes
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        return hashlib.sha256(str(self.index).encode() + str(self.timestamp).encode() + str(self.data).encode() + str(self.previous_hash).encode() + str(self.version_changes).encode()).hexdigest()


class BlockChain:
    def __init__(self, genesis_fasta):
        self.chain = [self.create_genesis_block(genesis_fasta)]

    def create_genesis_block(self, genesis_fasta):
        return Block(0, time.time(), {"id": "Genesis Block", "fasta": genesis_fasta}, "0", {"version-1": "Initial version"})

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data, version_changes):
        for block in self.chain:
            if block.data["id"] == data["id"]:
                block.version_changes.update(version_changes)
                return
        block = self.get_latest_block()
        index = block.index + 1
        timestamp = time.time()
        previous_hash = block.hash
        version_changes = version_changes.copy()
        version_changes.update(block.version_changes)
        block = Block(index, timestamp, data, previous_hash, version_changes)
        self.chain.append(block)

    def check_version(self, id, fasta):
        prev_fasta = ""
        found = False
        last_version = -1  # initialize last_version to -1
        for block in self.chain[::-1]:
            if block.data['id'] == id:
                found = True
                prev_fasta = self.get_latest_version(id)
                last_version = int(max(block.version_changes.keys()).split("-")[-1])
                break
        version = "version-1"
        change = f"Added new sequence: {fasta}"
        version_changes = {"version-1": change}
        if found:
            diff = set(prev_fasta).symmetric_difference(set(fasta))
            last_version = max(block.version_changes.keys(), key=lambda v: [int(x) for x in v.split('-')[1:]])
            last_version_num = int(last_version.split("-")[-1])
            if last_version_num == 10:
                version = "version-11"
            elif last_version_num == -1000:
                version = "version-1001"
            else:
                version = "version-" + str(last_version_num + 1)

            if len(fasta) > len(prev_fasta):
                for i in range(len(prev_fasta)):
                    if prev_fasta[i] != fasta[i]:
                        change = f"Replaced {prev_fasta[i]} with {fasta[i]} at position {i+1}"
                        break
                if not diff:
                    change = f"{fasta[len(prev_fasta):]} has been added at position {len(prev_fasta)+1}"
                else:
                    change = f"{diff.pop()} has been added at position {len(prev_fasta)+1}"
            elif len(fasta) < len(prev_fasta):
                for i in range(len(fasta)):
                    if prev_fasta[i] != fasta[i]:
                        change = f"Replaced {prev_fasta[i]} with {fasta[i]} at position {i+1}"
                        break
                if not diff:
                    change = f"{prev_fasta[len(fasta):]} has been removed from position {len(fasta)+1}"
                else:
                    change = f"{diff.pop()} has been removed from position {i+2}"
            else:
                for i in range(len(fasta)):
                    if prev_fasta[i] != fasta[i]:
                        change = f"Replaced {prev_fasta[i]} with {fasta[i]} at position {i+1}"
                        break
            version_changes = block.version_changes.copy()
            version_changes[version] = change
        self.add_block({"id": id, "fasta": fasta}, version_changes)
        return f"ID: {id}, Previous fasta: {prev_fasta}, Current fasta: {fasta}, Change:{change}, Version: {version}"



    def get_latest_version(self, id):
        for block in self.chain[::-1]:
            if block.data['id'] == id:
                return block.data['fasta']
        return ""

    def print_blockchain(self):
        for block in self.chain:
            print("Block #", block.index)
            print("Timestamp: ", block.timestamp)
            print("Data: ", block.data)
            print("Previous Hash: ", block.previous_hash)
            print("Hash: ", block.hash)
            print("Version Changes: ", block.version_changes)
            print()


