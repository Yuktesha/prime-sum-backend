from flask import Flask, request, jsonify
from flask_cors import CORS
import math
from typing import List, Dict, Optional

app = Flask(__name__)
# 配置 CORS，允許所有來源
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

def is_prime(n: int) -> bool:
    """判斷一個數是否為質數"""
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def find_prime_sequences(start: int, end: int, min_length: int, max_length: int) -> List[int]:
    """找出指定範圍內的所有質數"""
    return [n for n in range(max(2, start), end + 1) if is_prime(n)]

def find_consecutive_prime_sums(primes: List[int], target: int, min_length: int, max_length: int) -> List[List[int]]:
    """找出所有可以相加得到目標數的連續質數序列"""
    sequences = []
    n = len(primes)
    
    for length in range(min_length, min(max_length + 1, n + 1)):
        current_sum = sum(primes[:length])
        
        for i in range(n - length + 1):
            if i > 0:
                current_sum = current_sum - primes[i - 1] + primes[i + length - 1]
            
            if current_sum == target:
                sequences.append(primes[i:i + length])
            elif current_sum > target:
                break
    
    return sequences

@app.route('/api/search', methods=['POST'])
def search():
    """API endpoint for searching prime numbers"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '無效的請求數據'}), 400

        # 從請求中獲取參數，使用預設值
        start = int(data.get('start', 2))
        end = int(data.get('end', 100))
        min_sequences = int(data.get('min_sequences', 1))
        max_sequences = int(data.get('max_sequences', -1)) if data.get('max_sequences') != '∞' else -1
        min_length = int(data.get('min_length', 1))
        max_length = int(data.get('max_length', 10))

        # 驗證輸入
        if start < 2:
            return jsonify({'error': '起始值必須大於或等於 2'}), 400
        if end < start:
            return jsonify({'error': '結束值必須大於起始值'}), 400
        if min_length < 1:
            return jsonify({'error': '最小序列長度必須大於 0'}), 400
        if max_length < min_length:
            return jsonify({'error': '最大序列長度必須大於或等於最小序列長度'}), 400
        if min_sequences < 1:
            return jsonify({'error': '最小序列數量必須大於 0'}), 400
        if max_sequences != -1 and max_sequences < min_sequences:
            return jsonify({'error': '最大序列數量必須大於或等於最小序列數量'}), 400

        # 找出範圍內的所有質數
        primes = find_prime_sequences(2, end, min_length, max_length)
        results = []

        # 對每個質數尋找連續質數序列
        for prime in primes:
            if prime < start:
                continue
                
            sequences = find_consecutive_prime_sums(primes, prime, min_length, max_length)
            
            # 根據序列數量過濾結果
            if len(sequences) >= min_sequences:
                if max_sequences == -1 or len(sequences) <= max_sequences:
                    for seq in sequences:
                        results.append({
                            'sum': prime,
                            'sequence': seq
                        })

        # 按照前端期望的格式返回結果
        return jsonify({
            'results': results
        })

    except ValueError as e:
        return jsonify({'error': '請輸入有效的數值'}), 400
    except Exception as e:
        app.logger.error(f'Error in search endpoint: {str(e)}')
        return jsonify({'error': f'服務器錯誤：{str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
