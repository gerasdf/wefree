//
//  Database.h
//  wefree
//
//  Created by Eloy Adonis Colell on 28/03/14.
//  Copyright (c) 2014 WeFree. All rights reserved.
//

#import <Cocoa/Cocoa.h>

@interface Database : NSObject {
    NSString *filename;
    NSString *url;
    NSArray *data;
}

- (void) add: (NSMutableDictionary *) dictionary;
- (NSMutableDictionary *) find: (NSMutableDictionary *) query;
- (void) sync;

@end
