//
//  AppDelegate.h
//  wefree
//
//  Created by Eloy Adonis Colell on 26/03/14.
//  Copyright (c) 2014 WeFree. All rights reserved.
//

#import <Cocoa/Cocoa.h>
#import <CoreWLAN/CoreWLAN.h>
#import <CoreWLAN/CWNetwork.h>
#import "Database.h"

@interface AppDelegate : NSObject <NSApplicationDelegate> {
    NSBundle *bundle;
    NSImage *logo;
    IBOutlet NSMenu *statusMenu;
    NSStatusItem *statusItem;
    NSImage *statusImage;
    NSImage *statusHighlightImage;
    NSMutableDictionary *networks;
    Database *database;
}

//optional

- (IBAction) share: (id)sender;
- (IBAction) updateDatabase: (id)sender;
- (IBAction) rescan: (id)sender;
- (IBAction) wtf: (id)sender;
- (IBAction) connectTo: (id)sender;
- (BOOL) isAWeFree: (CWNetwork *)net;
- (NSImage *) getNetworkImageFor: (CWNetwork *)net;
- (void) backgroundNetworkUpdate;

@property (assign) IBOutlet NSWindow *window;

@end
