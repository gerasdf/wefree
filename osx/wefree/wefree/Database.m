//
//  Database.m
//  wefree
//
//  Created by Eloy Adonis Colell on 28/03/14.
//  Copyright (c) 2014 WeFree. All rights reserved.
//

#import "Database.h"

@implementation Database

- (id) init {
    self = [super init];
    if (self) {
        filename = @"wefree.app/aps.db";
        url = @"http://wefree.usla.org.ar/get";
        //application Documents dirctory path
        NSError *jsonError = nil;
        data = [self translate: [NSData dataWithContentsOfFile:filename options:kNilOptions error:&jsonError ]];
        if ([data count] == 0) {
            [self sync];
        }
    }
    return self;
}

- (void) add: (NSMutableDictionary *) dictionary {
    // After adding the data into the server should sync
    // [self sync];
}

- (NSMutableDictionary *) find: (NSMutableDictionary *) query {
    NSMutableDictionary *result = [NSMutableDictionary new];
    for (NSMutableDictionary *ap in data) {
        if ([[result allKeys] count] > 0) { break; }
        BOOL found = true;
        for (NSString *k in [query allKeys]) {
            BOOL equal = [[ap objectForKey: k] isEqualToString: [query objectForKey: k] ];
            found &= equal;
        }
        if (found) { result = ap; }
    }
    return result;
}

- (NSArray *) translate:(NSData *)binaryData {
    NSMutableString *jsonString = [[NSMutableString alloc] initWithData:binaryData encoding:NSUTF8StringEncoding];
    jsonString = (NSMutableString *)[jsonString stringByReplacingOccurrencesOfString: @"}\n{" withString:@"},{"];
    [jsonString insertString: @"[" atIndex:0];
    [jsonString appendString: @"]"];
    NSData *jsonData = [jsonString dataUsingEncoding:NSUTF8StringEncoding];
    NSError *error;
    return [NSJSONSerialization JSONObjectWithData:jsonData options:0 error:&error];
}

- (void) sync {
    // FUTURE: Should sync by incrementals versions (avoiding the download of the entire database.
    NSURLRequest *request = [NSURLRequest requestWithURL:[NSURL                                                           URLWithString: url]];
    NSData *responseData = [NSURLConnection sendSynchronousRequest:request
                                                 returningResponse: nil error:nil];
    [responseData writeToFile: filename atomically: true];
    data = [self translate: responseData];
}

@end
