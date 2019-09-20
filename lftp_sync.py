#!/usr/bin/python3
# --------------------------------------------------------
# Date: 31-01-2018
# Author: Mike Duke
#
# Sync ftp source to local directory
# Dependant on the lftp utility
# Add to crontab: 
# 01 */2 * * * /usr/scripts/lftp_sync.py >> /var/log/ftp_sync.log 2>&1
# This will then sync remote to local every 2 hours
#
# --------------------------------------------------------

import os
import datetime
import smtplib
import subprocess

def send_mail():
    log_file = open('/var/log/ftp_sync.log', 'r')
    log_msg = log_file.read()
    mail_srv = 'mail.my_email_domain.co.za'
    mail_port = '25'
    mail_name = 'ftp_sync@my_email_domain.co.za'
    mail_recip = ['person1@my_email_domain.co.za', 'person2@my_email_domain.co.za', 'person3@my_email_domain.co.za']
    mail_sub = 'Error with lftp sync on localprint-server'
    mail_msg = 'Subject: {}\n\n{}'.format(mail_sub, log_msg)
    smtpServ = smtplib.SMTP(mail_srv, mail_port)
    smtpServ.sendmail(mail_name, mail_recip, mail_msg)
    log_file.close()
    smtpServ.quit()
    print('Sending email notification to: %s' % mail_recip)

def sync():
    time = str(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
    tod_date = datetime.date.today()
    tom_date = tod_date + datetime.timedelta(days=1)
    date_list = [tod_date.strftime('%d%m%Y'), tom_date.strftime('%d%m%Y')]

    ftp_server = 'ip_address_of_ftp_server'
    ftp_user = 'anonymous'
    ftp_pass = 'anonymous'
    source_dir = 'data_dir'
    target_dir = '/some_where/'

    print()
    print('%s  starting ftp sync' % time)


    for day in date_list:
        try:

            ''' This is the old command using os module (this module can't catch exceptions)
            os.system('lftp -u %s,%s -e "mirror -c -v --parallel=5 /%s/%s %s" -p 21 %s <<EOF' % (ftp_user, ftp_pass, source_dir, day, target_dir, ftp_server))
            '''
            #TODO: use subprocess instead of os module to catch exceptions

            connect = ['lftp -u '+ ftp_user + ',' + ftp_pass + ' -e "mirror -c -v --parallel=5 /' + source_dir + '/' + day + ' '+ target_dir + '" -p 21 '+ ftp_server + ' <<EOF']
            res = subprocess.Popen(connect, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            output, error = res.communicate()
            error = error.decode('ascii')
            output = output.decode('ascii')
            err_550 = '550 No such file or directory'

            if output:
                print(time, " return code ", res.returncode)
                print(time, " Transfer output for:", day)
                print(output)
                print('%s  sync process complete!' % time)
                log_file = open('/var/log/ftp_sync.log', 'a')
                log_file.write('\n')
                log_file.write(' ')
                log_file.write(time)
                log_file.write('\n')
                log_file.write(str(output))
                log_file.write('\n')
                log_file.close()
            elif error:
                print(time, " return code ", res.returncode)
                e1 = time, " Error: ", error
                print(e1)
                print('%s  Error synchronizing the ftp source' % time)
                log_file = open('/var/log/ftp_sync.log', 'a')
                log_file.write('\n')
                log_file.write(str(e1))
                log_file.write('\n')
                log_file.close()
               
                if err_550 not in error:
                    send_mail()
                else:
                    print(day, ' might not be available yet')
            else:
                print(time, ' nothing to sync for:', day)
                log_file = open('/var/log/ftp_sync.log', 'a')
                log_file.write('\n')
                log_file.write(time)
                log_file.write(' ')
                log_file.write(' nothing to sync for: ')
                log_file.write(day)
                log_file.write('\n')
                log_file.close()

        except OSError as e:
            print('%s  Error synchronizing the ftp source' % time)

        
        try:
            print('%s  changing permissions...' % time)
            #TODO: use subprocess for changing permissions
            #subprocess.call(['chmod -R 600 /home/ftpusers/*'])
            os.system('chmod -R 600 /home/ftpusers/*')
        except perm_err as e:
            e1 = e
            print('%s  Error changing file permissions' % time)
            log_file = open('/var/log/ftp_sync.log', 'a')
            log_file.write(time)
            log_file.write(str(e1))
            log_file.write('\n')
            log_file.close()
            send_mail()
        

try:
    sync()
except:
    print('Something went wrong, check the log file /var/log/ftp_sync.log')
    send_mail()
