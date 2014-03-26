//
//  AppDelegate.h
//  wefree
//
//  Created by Eloy Adonis Colell on 26/03/14.
//  Copyright (c) 2014 WeFree. All rights reserved.
//

#import <Cocoa/Cocoa.h>

@interface AppDelegate : NSObject <NSApplicationDelegate> {
    NSImage *logo;
    IBOutlet NSMenu *statusMenu;
    NSStatusItem *statusItem;
    NSImage *statusImage;
    NSImage *statusHighlightImage;
}

//optional

- (IBAction) share: (id)sender;
- (IBAction) updateDatabase: (id)sender;
- (IBAction) rescan: (id)sender;
- (IBAction) wtf: (id)sender;

@property (assign) IBOutlet NSWindow *window;

@end
