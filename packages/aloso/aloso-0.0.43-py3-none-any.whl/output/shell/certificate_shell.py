import os

from OpenSSL import crypto

from domain.certificate_management import Certificate


class CertificateShell(Certificate):
    def create_key(self):
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 4096)
        return key

    def create_dir_and_init_key(self):
        os.system('mkdir -p ' + os.getenv('HOME') + '/Documents/keys')
        file = os.getenv('HOME') + '/Documents/keys/key.pem'
        key = self.create_key()
        open(file, 'wb').write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key, passphrase='12345678'))
        return file

    def create(self):
        self.create_dir_and_init_key()

        certFile = os.getenv('HOME') + '/Documents/certificate.pem'
        cert = crypto.X509()
        cert.get_subject().C = 'FR'
        cert.get_subject().ST = 'Indre-et-Loire'
        cert.get_subject().L = 'Tours'
        cert.get_subject().O = 'ExNovo'
        cert.get_subject().OU = 'IT'
        cert.get_subject().CN = 'Ex Novo Certificate'
        cert.get_subject().emailAddress = 'bacari.madi@exnovo.io'

        open(certFile, "wb").write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
