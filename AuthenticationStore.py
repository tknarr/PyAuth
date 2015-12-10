# -*- coding: utf-8 -*-

import wx

class AuthenticationStore:

    def __init__( self, filename ):
        self.cfg = wx.FileConfig( localFilename = filename,
                                  style = wx.CONFIG_USE_LOCAL_FILE )
        self.entry_list = []
        self.next_group = 1

        # TODO Read configuration entries into a list

        # Make sure they're sorted before creating the entry panels
        keyfunc = lambda x: x.GetSortIndex()
        self.entry_list.sort( key = keyfunc )


    def EntryList( self ):
        return self.entry_list

    
    def Regroup( self ):
        keyfunc = lambda x: x.GetSortIndex()
        self.entry_list.sort( key = keyfunc )
        # TODO remove existing groups from config
        i = 1
        for e in entry_list:
            e.SetGroup( i )
            e.UpdateIndex( i )
            i += 1
        self.next_group = i
        # TODO write entries into config with new group numbers


    # TODO Auth code text class methods
    # Methods: add an entry
    #          update an entry
    #          delete an entry


class AuthenticationEntry:

    def __init__( self, store, group, index, provider = "", account = "", secret = "" ):
        self.store = store
        self.group_number = group
        self.cfg_path = "/%s" % str( self.group_number )
        self.sort_index = index
        self.provider = provider
        self.account = account
        self.secret = secret


    def GetGroup( self ):
        return self.group_number

    def SetGroup( self, g ):
        self.group_number = g
        

    def GetIndex( self ):
        return self.sort_index

    def SetIndex( self, index ):
        self.store.WriteInt( self.cfgpath + "/sort_index", index )
        self.sort_index = index

    def UpdateIndex( self, index ):
        # We don't update the config here, this function is only called
        # from Regroup() and the last step there is to update the config
        # with the new information.
        self.sort_index = index
        
    def GetProvider( self );
        return self.provider
    
    def SetProvider( self, provider ):
        self.store.Write( self.cfgpath + "/provider", provider )
        self.provider = provider

    def GetAccount( self ):
        return self.account
    
    def SetAccount( self, account ):
        self.store.Write( self.cfgpath + "/account", account )
        self.account = account

    def GetSecret( self ):
        return self.secret
    
    def SetSecret( self, secret ):
        self.store.Write( self.cfgpath + "/secret", secret )
        self.secret = secret
