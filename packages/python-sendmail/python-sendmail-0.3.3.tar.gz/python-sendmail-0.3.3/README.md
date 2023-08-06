# python-sendmail


Sendmail client. send mail via stmp server.
 
## Install

```
pip install python-sendmail
```
    
## Installed Command Lines

- pysendmail

## Help

```
test@test ~ % pysendmail --help
Usage: pysendmail [OPTIONS] [CONTENT]

  Send mail.

Options:
  -f, --from-address TEXT  Mail sender, e.g. Name <name@example.com> or
                           name@example.com.  [required]
  -t, --to-address TEXT    Mail recipients, e.g. Name <name@example.com> or
                           name@example.com.  [required]
  -s, --subject TEXT       Mail subject
  -a, --attach TEXT        Mail attachments, allow multiple use.
  --html                   Mail content is HTML format.
  -e, --encoding TEXT      Encoding of the mail content input.
  -c, --charset TEXT       Encoding of the mail content output.
  -h, --host TEXT          Mail server address, default to 127.0.0.1.
  -p, --port INTEGER       Mail server port, default to 25. If you are using
                           an ssl server, mostly the port should be 465.
  --ssl                    Mail server using ssl encryption.
  -u, --user TEXT          Mail server login account. Empty user means don't
                           use login.
  -P, --password TEXT      Mail server login password. Empty password means
                           don't use login.
  --verify                 Verify ssl certificate.
  --help                   Show this message and exit.

```

## 使用案例


### Send mail with auth, without attachment.

- Mail sender：sender@example.com
- Mail recipient: recipient@exmaple.com
- Subject：just a test mail
- Content：just a test mail
- Mail Server Address：stmp.example.com
- Mail Server Port：465
- Use ssl: yes
- Account: sender@example.com
- Password: senderPassword
- Attachment: None

```
pysendmail -h stmp.example.com -p 465 --ssl -u sender@example.com -P senderPassword -f 'SENDER <sender@exmaple.com>' -t recipient@exmaple.com -s 'just a test mail' 'just a test mail'
```


### Send mail with attachment, without auth

- Mail sender：sender@example.com
- Mail recipient: recipient@exmaple.com
- Subject：just a test mail
- Content：just a test mail
- Mail Server Address：127.0.0.1
- Mail Server Port：25
- Use ssl: No
- Account: None
- Password: None
- Attachment: /path/to/attachment.pdf

```
pysendmail -f sender@exmaple.com -t recipient@exmaple.com -s 'just a test mail' -a /path/to/attachment.pdf 'just a test mail'
```

## Releases

### v0.3.3

- Fix ssl context problem.
- Add attach filename support.

### v0.3.2

- Add verify option. By default python-sendmail will ignore the ssl verify.

### v0.3.1

- Change help information to english.
- Use new style to release.

### v0.3.0

- Old style release.