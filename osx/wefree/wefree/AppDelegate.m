//
//  AppDelegate.m
//  wefree
//
//  Created by Eloy Adonis Colell on 26/03/14.
//  Copyright (c) 2014 WeFree. All rights reserved.
//

#import "AppDelegate.h"

@implementation AppDelegate

- (id) init {
    self = [super init];
    if (self) {
        database = [Database new];
    }
    return self;
}

- (void) awakeFromNib {
    statusItem = [[NSStatusBar systemStatusBar] statusItemWithLength: NSVariableStatusItemLength];
    
    bundle = [NSBundle mainBundle];

    statusImage = [[NSImage alloc] initWithContentsOfFile:[bundle pathForResource:@"wefree-192.0" ofType:@"png"]];
    logo = [[NSImage alloc] initWithContentsOfFile:[bundle pathForResource:@"wefree-192.0" ofType:@"png"]];
    [statusImage setSize: NSMakeSize(20,20)];
    [statusHighlightImage setSize: NSMakeSize(20,20)];
    [statusItem setImage: statusImage];
    [statusItem setAlternateImage: statusHighlightImage];
    [statusItem setMenu: statusMenu];
    [statusItem setHighlightMode: YES];
    [self backgroundNetworkUpdate];
}

- (void) backgroundNetworkUpdate {
    [[NSRunLoop currentRunLoop] performSelector:@selector(updateNetworks) target:self argument:statusMenu order:0 modes:[NSArray arrayWithObject:NSEventTrackingRunLoopMode]];
}

- (IBAction) share: (id)sender {
    NSLog(@"It should share");
}

- (IBAction) updateDatabase: (id)sender {
    NSLog(@"It should update the database");
    [database sync];
}

- (NSImage *) getNetworkImageFor: (CWNetwork *)net {
    NSInteger signal = [net rssiValue] - [net noiseMeasurement];
    NSString *cat;
    if (signal < 10) {
        cat = @"0";
    } else if (signal >= 10 && signal < 15) {
        cat = @"25";
    } else if (signal >= 15 && signal < 25) {
        cat = @"50";
    } else if (signal >= 25 && signal < 40) {
        cat = @"75";
    } else if (signal >= 40) {
        cat = @"100";
    }
    NSString *fileImage;
    if ([[[CWInterface interface] ssid] isEqualToString: [net ssid]]) {
        fileImage = @"connected";
    } else {
        NSString *name;
        if ([net supportsSecurity: 0]) {
            name = @"signals.";
        } else {
            if ([self isAWeFree: net]) {
                name = @"wefree-192.";
            } else {
                name = @"lock-signals-unknown.";
            }
        }
        fileImage = [NSString stringWithFormat: @"%@%@",name, cat];
    }
    NSImage *itemImage = [[NSImage alloc] initWithContentsOfFile:[bundle pathForResource: fileImage ofType:@"png"]];
    [itemImage setSize: NSMakeSize(20,20)];
    return itemImage;
}

- (void) updateNetworks {
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
            CWNetwork *net = [networks valueForKey: ssid];
            NSImage *itemImage = [self getNetworkImageFor: net];
            [item setImage: itemImage];
            NSInteger position = [[statusMenu itemArray] count] - 7;
            [statusMenu insertItem: item atIndex: position];
        }
    }
}

- (IBAction) rescan: (id)sender {
    [self backgroundNetworkUpdate];
}

- (IBAction) wtf: (id)sender {
    NSAlert *alert = [[NSAlert alloc] init];
    [alert setInformativeText: @"WeFree\nLet's free the WiFi."];
    [alert setMessageText: @"WeFreed networking"];
    [alert setIcon: logo];
    [alert runModal];
}

- (NSMutableDictionary *)getQuery:(CWNetwork *)net {
    NSMutableDictionary *dict = [NSMutableDictionary new];
    [dict setObject: [net bssid] forKey: @"bssid"];
    [dict setObject: [net ssid] forKey: @"essid"];
    return dict;
}

- (BOOL) isAWeFree: (CWNetwork *) net {
    NSMutableDictionary * result = [database find: [self getQuery:net]];
    return [[result allKeys] count] > 0;
}

- (IBAction) connectTo: (id)sender {
    CWNetwork *net = [networks valueForKey: [sender title]];
    NSMutableDictionary *ap = [database find: [self getQuery: net]];
    CWInterface *plug = [CWInterface interface];
    [plug associateToNetwork: net password: [[ap objectForKey: @"password"] firstObject] error: nil];
}

@end
