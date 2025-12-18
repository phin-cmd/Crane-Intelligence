"""
SSL/TLS Certificate Management
Handles certificate generation, validation, and renewal
"""

import os
import ssl
import logging
import subprocess
import datetime
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
import asyncio
import aiofiles

logger = logging.getLogger(__name__)

class SSLManager:
    """SSL/TLS Certificate Management System"""
    
    def __init__(self, cert_dir: str = "certs"):
        self.cert_dir = Path(cert_dir)
        self.cert_dir.mkdir(exist_ok=True)
        self.cert_file = self.cert_dir / "server.crt"
        self.key_file = self.cert_dir / "server.key"
        self.ca_file = self.cert_dir / "ca.crt"
        self.cert_expiry_days = 365
        self.renewal_threshold_days = 30
        
    async def generate_self_signed_certificate(self, 
                                              domain: str = "localhost",
                                              country: str = "US",
                                              state: str = "VA",
                                              city: str = "Richmond",
                                              organization: str = "Crane Intelligence",
                                              email: str = "admin@craneintelligence.tech") -> Tuple[str, str]:
        """Generate a self-signed SSL certificate"""
        try:
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
            # Create certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, country),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state),
                x509.NameAttribute(NameOID.LOCALITY_NAME, city),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
                x509.NameAttribute(NameOID.COMMON_NAME, domain),
                x509.NameAttribute(NameOID.EMAIL_ADDRESS, email),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                datetime.datetime.utcnow() + datetime.timedelta(days=self.cert_expiry_days)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(domain),
                    x509.DNSName("localhost"),
                    x509.IPAddress("127.0.0.1"),
                ]),
                critical=False,
            ).add_extension(
                x509.KeyUsage(
                    key_cert_sign=False,
                    crl_sign=False,
                    digital_signature=True,
                    content_commitment=False,
                    key_encipherment=True,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False
                ),
                critical=True,
            ).add_extension(
                x509.ExtendedKeyUsage([
                    x509.ExtendedKeyUsageOID.SERVER_AUTH,
                    x509.ExtendedKeyUsageOID.CLIENT_AUTH,
                ]),
                critical=True,
            ).sign(private_key, hashes.SHA256())
            
            # Save certificate and key
            cert_pem = cert.public_bytes(Encoding.PEM)
            key_pem = private_key.private_bytes(
                encoding=Encoding.PEM,
                format=PrivateFormat.PKCS8,
                encryption_algorithm=NoEncryption()
            )
            
            async with aiofiles.open(self.cert_file, 'wb') as f:
                await f.write(cert_pem)
            
            async with aiofiles.open(self.key_file, 'wb') as f:
                await f.write(key_pem)
            
            logger.info(f"Self-signed certificate generated for {domain}")
            return str(self.cert_file), str(self.key_file)
            
        except Exception as e:
            logger.error(f"Error generating self-signed certificate: {e}")
            raise
    
    async def validate_certificate(self, cert_path: str) -> Dict[str, Any]:
        """Validate SSL certificate"""
        try:
            with open(cert_path, 'rb') as f:
                cert_data = f.read()
            
            cert = x509.load_pem_x509_certificate(cert_data)
            
            # Check expiry
            now = datetime.datetime.utcnow()
            not_after = cert.not_valid_after.replace(tzinfo=None)
            days_until_expiry = (not_after - now).days
            
            # Check if certificate is valid
            is_valid = now < not_after
            
            # Check if renewal is needed
            needs_renewal = days_until_expiry <= self.renewal_threshold_days
            
            return {
                "valid": is_valid,
                "expires_at": not_after.isoformat(),
                "days_until_expiry": days_until_expiry,
                "needs_renewal": needs_renewal,
                "subject": str(cert.subject),
                "issuer": str(cert.issuer),
                "serial_number": str(cert.serial_number),
                "version": cert.version.name
            }
            
        except Exception as e:
            logger.error(f"Error validating certificate: {e}")
            return {
                "valid": False,
                "error": str(e)
            }
    
    async def renew_certificate(self, domain: str) -> bool:
        """Renew SSL certificate"""
        try:
            # Check if certificate exists and needs renewal
            if self.cert_file.exists():
                cert_info = await self.validate_certificate(str(self.cert_file))
                if cert_info.get("valid") and not cert_info.get("needs_renewal"):
                    logger.info("Certificate is still valid, no renewal needed")
                    return True
            
            # Generate new certificate
            cert_path, key_path = await self.generate_self_signed_certificate(domain)
            
            # Backup old certificate
            if self.cert_file.exists():
                backup_cert = self.cert_dir / f"server_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.crt"
                backup_key = self.cert_dir / f"server_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.key"
                
                await asyncio.gather(
                    aiofiles.os.rename(str(self.cert_file), str(backup_cert)),
                    aiofiles.os.rename(str(self.key_file), str(backup_key))
                )
            
            logger.info(f"Certificate renewed for {domain}")
            return True
            
        except Exception as e:
            logger.error(f"Error renewing certificate: {e}")
            return False
    
    async def setup_ssl_context(self) -> ssl.SSLContext:
        """Setup SSL context for HTTPS"""
        try:
            # Check if certificate exists
            if not self.cert_file.exists() or not self.key_file.exists():
                logger.info("Certificate not found, generating self-signed certificate")
                await self.generate_self_signed_certificate()
            
            # Validate certificate
            cert_info = await self.validate_certificate(str(self.cert_file))
            if not cert_info.get("valid"):
                logger.warning("Certificate is invalid, generating new one")
                await self.generate_self_signed_certificate()
            
            # Create SSL context
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(str(self.cert_file), str(self.key_file))
            
            # Configure SSL settings
            context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
            context.options |= ssl.OP_NO_SSLv2
            context.options |= ssl.OP_NO_SSLv3
            context.options |= ssl.OP_NO_TLSv1
            context.options |= ssl.OP_NO_TLSv1_1
            context.options |= ssl.OP_CIPHER_SERVER_PREFERENCE
            context.options |= ssl.OP_SINGLE_DH_USE
            context.options |= ssl.OP_SINGLE_ECDH_USE
            
            # Set minimum TLS version
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            
            logger.info("SSL context configured successfully")
            return context
            
        except Exception as e:
            logger.error(f"Error setting up SSL context: {e}")
            raise
    
    async def get_certificate_info(self) -> Dict[str, Any]:
        """Get comprehensive certificate information"""
        try:
            if not self.cert_file.exists():
                return {"error": "Certificate file not found"}
            
            cert_info = await self.validate_certificate(str(self.cert_file))
            
            # Get file sizes
            cert_size = self.cert_file.stat().st_size if self.cert_file.exists() else 0
            key_size = self.key_file.stat().st_size if self.key_file.exists() else 0
            
            return {
                **cert_info,
                "cert_file": str(self.cert_file),
                "key_file": str(self.key_file),
                "cert_size_bytes": cert_size,
                "key_size_bytes": key_size,
                "cert_dir": str(self.cert_dir)
            }
            
        except Exception as e:
            logger.error(f"Error getting certificate info: {e}")
            return {"error": str(e)}
    
    async def cleanup_old_certificates(self, keep_days: int = 30):
        """Clean up old certificate backups"""
        try:
            now = datetime.datetime.now()
            cutoff_date = now - datetime.timedelta(days=keep_days)
            
            cleaned_count = 0
            for file_path in self.cert_dir.glob("server_backup_*"):
                if file_path.stat().st_mtime < cutoff_date.timestamp():
                    file_path.unlink()
                    cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} old certificate files")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old certificates: {e}")
            return 0
