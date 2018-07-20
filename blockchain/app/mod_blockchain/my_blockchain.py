import hashlib
import json
import time
import requests
from urllib.parse import urlparse
from hashlib import sha256
from textwrap import dedent
from flask import Flask
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request

"""
前哈希为计算的前区块的哈希值，区块内不含哈希值，nonce是和前哈希做pow

new_block(self, nonce, previous_hash = None)
传入：封装随机数、前哈希值(创世区块)
返回：新区块

new_transaction(self, come, go, ver, seller, buyer, price, amount, app1, app2 = None):
传入：come两位,go两位，ver两位，seller和buyer都是用户名称
#返回：区块数+1

hash(block)：计算给定的block的哈希值
返回：十六进制的字符串

proof_of_work(self, hash:str):挖矿
返回：nonce

new_node(self, address)：新建用户节点

valid_chain(self, chain)：判断chain是否合法
返回：合法True否则False

valid_chains(self)：获取整个网络节点的合法链
返回：有替换返回True反之False
"""


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.nodes = set()
        self.cur_transactions = []
        # 当前交易总数
        self.num = 0
        # 创建创世区块
        self.new_block(nonce=self.proof_of_work('1'), previous_hash='1')

    def new_block(self, nonce, previous_hash):
        block = {
            # int
            'index': len(self.chain) + 1,
            # str
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
            'timestamp': time(),
            # 数组
            'transactions': self.cur_transactions,
            # int
            'nonce': nonce,
        }

        # 重置当前交易栏
        self.cur_transactions = []

        self.chain.append(block)
        return block

    """生成新交易，新内容将暂存至cur_transactions"""
    def new_transaction(self, come, go, ver, seller, buyer, price, amount, app1, app2=None):
        self.cur_transactions.append({
            # int
            'index': come + go + "%06d" % self.num + ver,
            # int
            'ver': ver,
            'time': time(),
            # int
            'seller': seller,
            # double
            'price': price,
            # int
            'buyer': buyer,
            # int
            'amount': amount,
            'app1': app1,
            # 当是商家和物流时怎么处理？
            'app2': app2 or 0
        })

        self.num += 1

        return self.last_block['index'] + 1

    """计算hash值"""
    @staticmethod
    def hash(block) -> str:
        tem_str = json.dumps(block, sort_keys=True).encode()
        return sha256(tem_str).hexdigest()

    """挖矿"""
    @staticmethod
    def proof_of_work(hash_value: str)->int:
        nonce = 0
        while True:
            guess = f'{hash_value}{nonce}'.encode()
            guess_hash = hashlib.sha256(guess).hexdigest()
            if guess_hash[:4] == "0000":
                break
            nonce += 1
        return nonce

    """新建新节点"""
    def new_node(self, address: str) -> None:
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    """判断传入区块链是否是合法的"""
    def valid_chain(self, chain):

        pre = chain[0]
        index = 1

        while index < len(chain):
            block = chain[index]
            # 判断前哈希值是否正确
            if self.hash(pre) != block['previous_hash']:
                return False

            # 判断工作机制是否正确
            previous_hash = pre['previous_hash']
            nonce = pre['nonce']
            guess = f'{previous_hash}{nonce}'.encode()
            guess_hash = hashlib.sha256(guess).hexdigest()
            if guess_hash[:4] != "0000":
                return False

            pre = block
            index += 1

        return True

    """获取整个网络节点中合法的区块链"""
    def valid_chains(self):

        new_chain = None
        max_length = len(self.chain)

        # 对网络中所有节点进行查找，这儿使用requests框架中的命令，需要改为P2P
        for node in self.nodes:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # 当找到一条长度比当前长且合法的链
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # 如果找到新的链，则替换掉它
        if new_chain:
            self.chain = new_chain
            return True

        return False

    """返回最后一个block"""
    @property
    def last_block(self):
        return self.chain[-1]

    """总挖矿函数"""
    def mine(self) ->bool:
        if not self.cur_transactions:
            return False

        pre_block = self.last_block

        last_hash = self.hash(pre_block)
        nonce = self.proof_of_work(last_hash)

        # block未使用
        block = self.new_block(nonce=nonce, previous_hash=last_hash)

        # 广播，未完成
        # announce_new_block(new_block)
        return True

# 实例化节点
app = Flask(__name__)

# 为这个节点生成一个全局唯一的地址
node_identifier = str(uuid4()).replace('-', '')

# 实例化区块链类
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    statue = blockchain.mine()
    if not statue:
        return 'Missing values', 400
    response = {
        'message': "New Block Forged",
        'index': blockchain.last_block['index'],
        'transactions': blockchain.last_block['transactions'],
        'nonce': blockchain.last_block['nonce'],
        'previous_hash': blockchain.last_block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])  # 创建/transactions/new POST接口,可以给接口发送交易数据.
def new_transaction():
    values = request.get_json()

    # 检查所需字段是否在POST'ed数据中
    required = ['come','go','ver','seller', 'buyer', 'price','amount','app1','app2']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # 创建一个新交易
    index = blockchain.new_transaction(values['come'], values['go'], values['ver'],  values['seller'], values['buyer'],
                                       values['price'], values['amount'], values['app1'], values['app2'],)

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])  # 创建 /chain 接口, 返回整个区块链。
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def new_node():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.new_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)  # 服务运行在端口上

