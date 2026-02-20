from solders.keypair import Keypair

# 私钥字节数组
private_key_bytes = [121, 159, 226, 232, 193, 168, 47, 111, 192, 23, 78, 230, 89, 141, 47, 77, 204, 200, 111, 228, 241, 238, 167, 149, 157, 155, 110, 107, 116, 238, 15, 153, 5, 201, 21, 57, 82, 221, 6, 56, 187, 65, 202, 227, 219, 207, 206, 143, 215, 58, 0, 202, 17, 145, 129, 41, 106, 115, 250, 140, 221, 184, 125, 225]
# 创建密钥对
keypair = Keypair.from_bytes(bytes(private_key_bytes))

# 获取公钥
public_key = keypair.pubkey()

print("私钥:", keypair)