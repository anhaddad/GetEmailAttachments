# GetEmailAttachments
A python program which downloads all the attachment from an email

# Quick start
1. Enter the EMAIL-SERVER, EMAIL-ADDRESS, EMAIL-PASSWORD in line 200 and 201
2. If you are using your gmail address set "Allow less secure apps: ON" here https://goo.gl/X2kgfH
3. Execute the program

# Manual
In the object named "my_email" at the bottom the possible values of the variables are;

EMAIL-SERVER (eg. imap.gmail.com)
EMAIL-ADDRESS (eg. youmail@gmail.com)
EMAIL-PASSWORD (your email password)
inbox ( it can change to Sent, Trash etc)
download_folder (The program will use the OS environment temp folder where the attachments will be saved. You can change it to  anything you want in quotes eg. m.save_attachment("c:\tmp") )

filter="All" (It can set to UnSeen, Seen, All so the program fetches from unread, read or all emails)

# Fetch with filters

change the snippet 

                    # if em.header.pass_filter(sender, sbj_chg, sbj_new) == "new":
                        # self.msglist.append(em) #Commend it out if you want to go with the yield.
                    yield em # With this line we check and save the progress.
                    # else:
                    #     continue
                    
  to
                    
                    if em.header.pass_filter(sender, sbj_chg, sbj_new) == "new":
                        # self.msglist.append(em) #Commend it out if you want to go with the yield.
                        yield em # With this line we check and save the progress.
                    else:
                        continue

senders-email
starts-with-1
starts-with-2

Advanced
    def select_inbox(self, inbox, ro=True):
    
In the above line, ro can be True or False. False marks email as read. True doesn't change their status.
