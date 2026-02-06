"""
Public Key Infrastructure (PKI) Management
Handles certificate generation, storage, and validation
Uses RSA keys and X.509 certificates
"""

import os
import logging
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import base64
import json

logger = logging.getLogger(__name__)

class PKIManager:
    """Manage PKI certificates and keys"""
    
    def __init__(self, certs_dir='certs'):
        """Initialize PKI manager"""
        self.certs_dir = certs_dir
        self.default_backend = default_backend()
        
        # Create certs directory if it doesn't exist
        os.makedirs(certs_dir, exist_ok=True)
        os.makedirs(os.path.join(certs_dir, 'ca'), exist_ok=True)
        os.makedirs(os.path.join(certs_dir, 'server'), exist_ok=True)
        os.makedirs(os.path.join(certs_dir, 'client'), exist_ok=True)
        os.makedirs(os.path.join(certs_dir, 'crls'), exist_ok=True)
    
    def generate_private_key(self, key_size=2048):
        """Generate RSA private key"""
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=self.default_backend
        )
    
    def generate_ca_certificate(self, common_name='Admin Dashboard CA', 
                               validity_days=3650, country='US', 
                               state='CA', locality='San Francisco', 
                               organization='Security'):
        """Generate CA (Certificate Authority) certificate"""
        
        # Generate private key
        ca_key = self.generate_private_key()
        
        # Create certificate subject and issuer
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, country),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state),
            x509.NameAttribute(NameOID.LOCALITY_NAME, locality),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])
        
        # Build certificate
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            ca_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=validity_days)
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_cert_sign=True,
                crl_sign=True,
                key_encipherment=False,
                content_commitment=False,
                data_encipherment=False,
                key_agreement=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).sign(ca_key, hashes.SHA256(), self.default_backend)
        
        # Save CA certificate and key
        self._save_certificate(cert, 'ca/ca.crt')
        self._save_private_key(ca_key, 'ca/ca.key')
        
        logger.info("CA certificate and key generated successfully")
        return cert, ca_key
    
    def generate_server_certificate(self, common_name='localhost', 
                                   san_list=None, validity_days=365):
        """Generate server certificate signed by CA"""
        
        # Load CA certificate and key
        try:
            ca_cert, ca_key = self._load_ca_cert()
        except FileNotFoundError:
            logger.error("CA certificate not found. Generate CA first.")
            raise
        
        # Generate server private key
        server_key = self.generate_private_key()
        
        # Create certificate subject
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, 'US'),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, 'CA'),
            x509.NameAttribute(NameOID.LOCALITY_NAME, 'San Francisco'),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'Security'),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])
        
        # Build certificate
        builder = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            ca_cert.issuer
        ).public_key(
            server_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=validity_days)
        ).add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                content_commitment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        
        # Add SAN extension
        if san_list:
            san_list = [x509.DNSName(san) for san in san_list]
        else:
            san_list = [x509.DNSName(common_name)]
        
        builder = builder.add_extension(
            x509.SubjectAlternativeName(san_list),
            critical=False,
        )
        
        # Sign with CA key
        cert = builder.sign(ca_key, hashes.SHA256(), self.default_backend)
        
        # Save certificate and key
        self._save_certificate(cert, 'server/server.crt')
        self._save_private_key(server_key, 'server/server.key')
        
        logger.info(f"Server certificate generated for {common_name}")
        return cert, server_key
    
    def generate_client_certificate(self, common_name, validity_days=365):
        """Generate client certificate for authentication"""
        
        # Load CA certificate and key
        try:
            ca_cert, ca_key = self._load_ca_cert()
        except FileNotFoundError:
            logger.error("CA certificate not found. Generate CA first.")
            raise
        
        # Generate client private key
        client_key = self.generate_private_key()
        
        # Create certificate subject
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, 'US'),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, 'CA'),
            x509.NameAttribute(NameOID.LOCALITY_NAME, 'San Francisco'),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'Security'),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])
        
        # Build certificate
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            ca_cert.issuer
        ).public_key(
            client_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=validity_days)
        ).add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                content_commitment=True,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).sign(ca_key, hashes.SHA256(), self.default_backend)
        
        # Save certificate and key
        cert_path = f'client/{common_name}.crt'
        key_path = f'client/{common_name}.key'
        self._save_certificate(cert, cert_path)
        self._save_private_key(client_key, key_path)
        
        logger.info(f"Client certificate generated for {common_name}")
        return cert, client_key, cert_path, key_path
    
    def verify_certificate(self, cert_path, ca_cert_path=None):
        """Verify certificate signature and validity"""
        try:
            cert = self._load_certificate(cert_path)
            
            # Check expiration
            if datetime.utcnow() > cert.not_valid_after:
                logger.warning(f"Certificate {cert_path} has expired")
                return False, "Certificate expired"
            
            if datetime.utcnow() < cert.not_valid_before:
                logger.warning(f"Certificate {cert_path} not yet valid")
                return False, "Certificate not yet valid"
            
            # Verify signature with CA cert if provided
            if ca_cert_path:
                ca_cert = self._load_certificate(ca_cert_path)
                try:
                    # Use the public key from CA to verify the certificate
                    ca_cert.public_key().verify(
                        cert.signature,
                        cert.tbs_certificate_bytes,
                        cert.signature_algorithm_oid
                    )
                except Exception as e:
                    logger.warning(f"Certificate {cert_path} signature verification failed: {e}")
                    return False, "Signature verification failed"
            
            return True, "Certificate valid"
        
        except Exception as e:
            logger.error(f"Certificate verification error: {e}")
            return False, str(e)
    
    def _save_certificate(self, cert, filename):
        """Save certificate to file"""
        path = os.path.join(self.certs_dir, filename)
        with open(path, 'wb') as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        logger.debug(f"Certificate saved to {path}")
    
    def _save_private_key(self, key, filename):
        """Save private key to file"""
        path = os.path.join(self.certs_dir, filename)
        with open(path, 'wb') as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            ))
        # Set restrictive permissions
        os.chmod(path, 0o600)
        logger.debug(f"Private key saved to {path}")
    
    def _load_certificate(self, filename):
        """Load certificate from file"""
        path = os.path.join(self.certs_dir, filename)
        with open(path, 'rb') as f:
            return x509.load_pem_x509_certificate(
                f.read(), self.default_backend
            )
    
    def _load_ca_cert(self):
        """Load CA certificate and key"""
        ca_cert = self._load_certificate('ca/ca.crt')
        ca_key = self._load_private_key('ca/ca.key')
        return ca_cert, ca_key
    
    def _load_private_key(self, filename):
        """Load private key from file"""
        path = os.path.join(self.certs_dir, filename)
        with open(path, 'rb') as f:
            return serialization.load_pem_private_key(
                f.read(), password=None, backend=self.default_backend
            )
    
    def generate_certificate_chain(self):
        """Generate complete PKI certificate chain"""
        logger.info("Generating PKI certificate chain...")
        
        # Generate CA
        ca_cert, ca_key = self.generate_ca_certificate()
        
        # Generate server certificate
        server_cert, server_key = self.generate_server_certificate(
            common_name='localhost',
            san_list=['localhost', '127.0.0.1', 'admin.local']
        )
        
        logger.info("PKI certificate chain generated successfully")
        return {
            'ca_certificate': 'ca/ca.crt',
            'server_certificate': 'server/server.crt',
            'server_key': 'server/server.key'
        }

def get_pki_manager():
    """Get PKI manager instance"""
    from flask import current_app
    
    if 'pki_manager' not in current_app.config:
        current_app.config['pki_manager'] = PKIManager()
    
    return current_app.config['pki_manager']
