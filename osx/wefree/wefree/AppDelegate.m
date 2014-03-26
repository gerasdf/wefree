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
}

- (IBAction) share: (id)sender {
    NSLog(@"It should share");
}

- (IBAction) wtf: (id)sender {
    NSAlert *alert = [[NSAlert alloc] init];
    [alert setInformativeText: @"WeFree\nLet's free the WiFi."];
    [alert setMessageText: @"WeFreed networking"];
    [alert setIcon: logo];
    [alert runModal];
    NSLog(@"It should WTF!!");
}

@end
