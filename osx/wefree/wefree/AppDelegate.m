//
//  AppDelegate.m
//  wefree
//
//  Created by Eloy Adonis Colell on 26/03/14.
//  Copyright (c) 2014 WeFree. All rights reserved.
//

#import "AppDelegate.h"

@implementation AppDelegate

- (void) awakeFromNib {
    
    statusItem = [[NSStatusBar systemStatusBar] statusItemWithLength: NSVariableStatusItemLength];
    
    NSBundle *bundle = [NSBundle mainBundle];

    statusImage = [[NSImage alloc] initWithContentsOfFile:[bundle pathForResource:@"wefree-192.0" ofType:@"png"]];
    logo = [[NSImage alloc] initWithContentsOfFile:[bundle pathForResource:@"wefree-192.0" ofType:@"png"]];
    
    [statusItem setImage: statusImage];
    [statusItem setAlternateImage: statusHighlightImage];
    [statusItem setMenu: statusMenu];
    [statusItem setHighlightMode: YES];
    [[NSRunLoop currentRunLoop] performSelector:@selector(updateNetworks) target:self argument:statusMenu order:0 modes:[NSArray arrayWithObject:NSEventTrackingRunLoopMode]];
}

- (IBAction) share: (id)sender {
    NSLog(@"It should share");
}

- (IBAction) updateDatabase: (id)sender {
    NSLog(@"It should update the database");
}

- (void)updateNetworks {
    @autoreleasepool {
        CWInterface *currentInterface = [CWInterface interface];
        NSArray *nets = [[currentInterface scanForNetworksWithName:nil error:nil] allObjects];
        for (NSMenuItem *item in [statusMenu itemArray]) {
            if ([[statusMenu itemArray] count] > 7) {
                [statusMenu removeItem: item];
            }
        }
        networks = [NSMutableDictionary dictionary];
        for (CWNetwork *net in nets) {
            [networks setObject: net forKey: [net ssid]];
        }
        NSArray *sortedArray = [[networks allKeys] sortedArrayUsingSelector: @selector(localizedCaseInsensitiveCompare:)];
        for (NSString *ssid in sortedArray) {
            NSMenuItem *item = [[NSMenuItem alloc] initWithTitle: ssid action:@selector(connectTo:) keyEquivalent:@""];
            NSInteger position = [[statusMenu itemArray] count] - 7;
            [statusMenu insertItem: item atIndex: position];
        }
    }
}

- (IBAction) rescan: (id)sender {
    NSLog(@"It should rescan");
    [self updateNetworks];
}

- (IBAction) wtf: (id)sender {
    NSAlert *alert = [[NSAlert alloc] init];
    [alert setInformativeText: @"WeFree\nLet's free the WiFi."];
    [alert setMessageText: @"WeFreed networking"];
    [alert setIcon: logo];
    [alert runModal];
    NSLog(@"It should WTF!!");
}

- (IBAction) connectTo: (id)sender {
    NSLog(@"It should connect to a specific wifi!!");
}

@end
