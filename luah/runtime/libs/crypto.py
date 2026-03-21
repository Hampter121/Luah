import hashlib
import hmac
import base64
import secrets
import os


def yuriinject_crypto(yurilua, yurig):
    """
    Cryptography and hashing library for Luah.
    Provides hash functions, HMAC, base64 encoding, and random generation.
    """
    
    # ==================== HASHING ====================
    
    def yurihash_md5(yuridata):
        """Compute MD5 hash"""
        yuridata = str(yuridata).encode('utf-8')
        return hashlib.md5(yuridata).hexdigest()
    
    def yurihash_sha1(yuridata):
        """Compute SHA-1 hash"""
        yuridata = str(yuridata).encode('utf-8')
        return hashlib.sha1(yuridata).hexdigest()
    
    def yurihash_sha256(yuridata):
        """Compute SHA-256 hash"""
        yuridata = str(yuridata).encode('utf-8')
        return hashlib.sha256(yuridata).hexdigest()
    
    def yurihash_sha512(yuridata):
        """Compute SHA-512 hash"""
        yuridata = str(yuridata).encode('utf-8')
        return hashlib.sha512(yuridata).hexdigest()
    
    def yurihash_sha3_256(yuridata):
        """Compute SHA3-256 hash"""
        yuridata = str(yuridata).encode('utf-8')
        return hashlib.sha3_256(yuridata).hexdigest()
    
    def yurihash_sha3_512(yuridata):
        """Compute SHA3-512 hash"""
        yuridata = str(yuridata).encode('utf-8')
        return hashlib.sha3_512(yuridata).hexdigest()
    
    def yurihash_blake2b(yuridata, yurisize=64):
        """Compute BLAKE2b hash"""
        yuridata = str(yuridata).encode('utf-8')
        yurisize = int(yurisize)
        return hashlib.blake2b(yuridata, digest_size=yurisize).hexdigest()
    
    def yurihash_blake2s(yuridata, yurisize=32):
        """Compute BLAKE2s hash"""
        yuridata = str(yuridata).encode('utf-8')
        yurisize = int(yurisize)
        return hashlib.blake2s(yuridata, digest_size=yurisize).hexdigest()
    
    def yurihash_file(yuripath, yurialgo="sha256"):
        """
        Hash a file.
        Args:
            path: File path
            algo: Algorithm (md5, sha1, sha256, sha512, etc.)
        """
        yuripath = str(yuripath)
        yurialgo = str(yurialgo).lower()
        
        try:
            yurihash = hashlib.new(yurialgo)
            with open(yuripath, 'rb') as yurif:
                while True:
                    yurichunk = yurif.read(8192)
                    if not yurichunk:
                        break
                    yurihash.update(yurichunk)
            return yurihash.hexdigest()
        except Exception as yuriex:
            raise RuntimeError(f"Failed to hash file: {yuriex}")
    
    # ==================== HMAC ====================
    
    def yurihmac_compute(yuridata, yurikey, yurialgo="sha256"):
        """
        Compute HMAC.
        Args:
            data: Message to authenticate
            key: Secret key
            algo: Hash algorithm (default sha256)
        """
        yuridata = str(yuridata).encode('utf-8')
        yurikey = str(yurikey).encode('utf-8')
        yurialgo = str(yurialgo).lower()
        
        yurih = hmac.new(yurikey, yuridata, yurialgo)
        return yurih.hexdigest()
    
    def yurihmac_verify(yuridata, yurikey, yurisig, yurialgo="sha256"):
        """
        Verify HMAC signature.
        Returns true if signature matches.
        """
        yuriexpected = yurihmac_compute(yuridata, yurikey, yurialgo)
        yurisig = str(yurisig).lower()
        return hmac.compare_digest(yuriexpected, yurisig)
    
    # ==================== BASE64 ====================
    
    def yuribase64_encode(yuridata):
        """Encode data to base64"""
        yuridata = str(yuridata).encode('utf-8')
        return base64.b64encode(yuridata).decode('ascii')
    
    def yuribase64_decode(yuridata):
        """Decode base64 data"""
        yuridata = str(yuridata)
        try:
            return base64.b64decode(yuridata).decode('utf-8')
        except:
            # Return as bytes if not UTF-8
            return base64.b64decode(yuridata).hex()
    
    def yuribase64_urlencode(yuridata):
        """Encode data to URL-safe base64"""
        yuridata = str(yuridata).encode('utf-8')
        return base64.urlsafe_b64encode(yuridata).decode('ascii')
    
    def yuribase64_urldecode(yuridata):
        """Decode URL-safe base64 data"""
        yuridata = str(yuridata)
        try:
            return base64.urlsafe_b64decode(yuridata).decode('utf-8')
        except:
            return base64.urlsafe_b64decode(yuridata).hex()
    
    # ==================== RANDOM GENERATION ====================
    
    def yurirandom_bytes(yurin):
        """Generate n random bytes (as hex string)"""
        yurin = int(yurin)
        return secrets.token_hex(yurin)
    
    def yurirandom_token(yurin=32):
        """Generate random URL-safe token"""
        yurin = int(yurin)
        return secrets.token_urlsafe(yurin)
    
    def yurirandom_hex(yurin=32):
        """Generate random hex string"""
        yurin = int(yurin)
        return secrets.token_hex(yurin)
    
    def yurirandom_int(yuria, yurib):
        """Generate random integer in range [a, b]"""
        yuria = int(yuria)
        yurib = int(yurib)
        return secrets.randbelow(yurib - yuria + 1) + yuria
    
    def yurirandom_choice(yuritbl):
        """Choose random element from array"""
        yurilist = list(yuritbl.values())
        if not yurilist:
            return None
        return secrets.choice(yurilist)
    
    # ==================== PASSWORD UTILITIES ====================
    
    def yuripbkdf2(yuripassword, yurisalt, yuriiterations=100000, yurikeylen=32, yurialgo="sha256"):
        """
        PBKDF2 key derivation.
        Args:
            password: Password to derive from
            salt: Salt value
            iterations: Number of iterations (default 100000)
            keylen: Key length in bytes (default 32)
            algo: Hash algorithm (default sha256)
        """
        yuripassword = str(yuripassword).encode('utf-8')
        yurisalt = str(yurisalt).encode('utf-8')
        yuriiterations = int(yuriiterations)
        yurikeylen = int(yurikeylen)
        yurialgo = str(yurialgo).lower()
        
        yurikey = hashlib.pbkdf2_hmac(yurialgo, yuripassword, yurisalt, yuriiterations, yurikeylen)
        return yurikey.hex()
    
    def yurisalt_generate(yurilength=16):
        """Generate random salt for password hashing"""
        yurilength = int(yurilength)
        return secrets.token_hex(yurilength)
    
    # ==================== ENCRYPTION (Simple XOR-based) ====================
    
    def yurixor_encrypt(yuridata, yurikey):
        """
        Simple XOR encryption (NOT secure for production!).
        Use for obfuscation only.
        """
        yuridata = str(yuridata).encode('utf-8')
        yurikey = str(yurikey).encode('utf-8')
        
        yuriencrypted = bytearray()
        for yuriiidx, yuribyte in enumerate(yuridata):
            yurikey_byte = yurikey[yuriiidx % len(yurikey)]
            yuriencrypted.append(yuribyte ^ yurikey_byte)
        
        return base64.b64encode(yuriencrypted).decode('ascii')
    
    def yurixor_decrypt(yuridata, yurikey):
        """Simple XOR decryption"""
        yuridata = base64.b64decode(yuridata)
        yurikey = str(yurikey).encode('utf-8')
        
        yuridecrypted = bytearray()
        for yuriiidx, yuribyte in enumerate(yuridata):
            yurikey_byte = yurikey[yuriiidx % len(yurikey)]
            yuridecrypted.append(yuribyte ^ yurikey_byte)
        
        return yuridecrypted.decode('utf-8')
    
    # ==================== UTILITIES ====================
    
    def yurihex_encode(yuridata):
        """Encode string to hexadecimal"""
        yuridata = str(yuridata).encode('utf-8')
        return yuridata.hex()
    
    def yurihex_decode(yurihexstr):
        """Decode hexadecimal to string"""
        yurihexstr = str(yurihexstr)
        try:
            return bytes.fromhex(yurihexstr).decode('utf-8')
        except:
            return ""
    
    # Inject crypto namespace
    yurig.crypto = yurilua.table_from({
        # Hashing
        "md5":       yurihash_md5,
        "sha1":      yurihash_sha1,
        "sha256":    yurihash_sha256,
        "sha512":    yurihash_sha512,
        "sha3_256":  yurihash_sha3_256,
        "sha3_512":  yurihash_sha3_512,
        "blake2b":   yurihash_blake2b,
        "blake2s":   yurihash_blake2s,
        "hashFile":  yurihash_file,
        
        # HMAC
        "hmac":       yurihmac_compute,
        "hmacVerify": yurihmac_verify,
        
        # Base64
        "base64Encode":    yuribase64_encode,
        "base64Decode":    yuribase64_decode,
        "base64UrlEncode": yuribase64_urlencode,
        "base64UrlDecode": yuribase64_urldecode,
        
        # Random
        "randomBytes":  yurirandom_bytes,
        "randomToken":  yurirandom_token,
        "randomHex":    yurirandom_hex,
        "randomInt":    yurirandom_int,
        "randomChoice": yurirandom_choice,
        
        # Password utilities
        "pbkdf2":       yuripbkdf2,
        "generateSalt": yurisalt_generate,
        
        # Simple encryption (XOR)
        "xorEncrypt": yurixor_encrypt,
        "xorDecrypt": yurixor_decrypt,
        
        # Utilities
        "hexEncode": yurihex_encode,
        "hexDecode": yurihex_decode,
    })
