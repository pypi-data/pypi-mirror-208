#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig


def __InitParser(parser):
    parser.add_argument("-i", "--login", help="Interactive login", action="store_true")
    parser.add_argument("--refresh", help="Refresh access token from previous login", action="store_true")
    parser.add_argument("--preferapikey", help="Prefere api key", action="store_true")
    parser.add_argument("--prefertoken", help="Prefere access token", action="store_true")
    parser.add_argument("--show", help="Show login information", action="store_true")
    parser.add_argument("--clearlogin", help="Clear login information", action="store_true")
    parser.add_argument("--clearapikey", help="Clear apikey information", action="store_true")

def main():
    args = ClientArgs.ParseApiKey(description="Interactive login", init=__InitParser)
    ClientConfig.UpdateEnvironmentFromConfiguration(args, args.config)

    if args.show:
        print(f"Configuration from {ClientConfig.GetConfigurationFilePath(args.config)}")
        envObj = ClientConfig.GetEnvironment(args.environment, args.config)
        tokeninfo = ClientConfig.GetAccessTokenInfo(envObj)
        fmt = "{!s:12}\t{}"
        print(fmt.format("environment", args.environment))
        print(fmt.format("username", ClientConfig.GetUsername(tokeninfo)))
        print(fmt.format("expires", ClientConfig.GetExpiresOn(tokeninfo)))
        print(fmt.format("isexpired", ClientConfig.IsExpired(tokeninfo)))
        print(fmt.format("apikey", ClientConfig.GetApiKey(envObj)))
        print(fmt.format("preferapikey", ClientConfig.GetPreferApiKey(envObj)))
    elif args.clearlogin or args.clearapikey:
        ClientConfig.ClearInfo(args.environment, clearlogin=args.clearlogin, clearapikey=args.clearapikey, configname=args.config)
    else:
        if args.login:
            from dhi.platform.authentication import ClientAuthentication
            (tokeninfo, _) = ClientAuthentication.AcquireTokenInteractively(args.environment)
            if tokeninfo:
                ClientConfig.SaveUserTokenInfo(args.environment, tokeninfo, args.config)
                username = tokeninfo.get("username")
                expireson = ClientConfig.GetExpiresOn(tokeninfo)
                fmt = "{!s:8}\t{}"
                print(fmt.format("environment", args.environment))
                print(fmt.format("username", username))
                print(fmt.format("expires", expireson))
        elif args.refresh:
            from dhi.platform.authentication import ClientAuthentication
            envObj = ClientConfig.GetEnvironment(args.environment, args.config)
            tokeninfo = ClientConfig.GetAccessTokenInfo(envObj)
            if not tokeninfo:
                print("ERROR: No access token to renew!")
            else:
                (tokeninfo, _) = ClientAuthentication.RefreshToken(args.environment, tokeninfo)
                if tokeninfo:
                    ClientConfig.SaveUserTokenInfo(args.environment, tokeninfo, args.config)
                    username = tokeninfo.get("username")
                    expireson = ClientConfig.GetExpiresOn(tokeninfo)
                    fmt = "{!s:8}\t{}"
                    print(fmt.format("environment", args.environment))
                    print(fmt.format("username", username))
                    print(fmt.format("expires", expireson))
                    print(fmt.format("isexpired", ClientConfig.IsExpired(tokeninfo)))
        elif args.prefertoken:
            ClientConfig.SetPreferApiKey(args.environment, False, args.config)
            envObj = ClientConfig.GetEnvironment(args.environment, args.config)
            tokeninfo = ClientConfig.GetAccessTokenInfo(envObj)
            if tokeninfo:
                username = tokeninfo.get("username")
                expireson = ClientConfig.GetExpiresOn(tokeninfo)
                fmt = "{!s:8}\t{}"
                print(fmt.format("environment", args.environment))
                print(fmt.format("username", username))
                print(fmt.format("expires", expireson))
                print(fmt.format("isexpired", ClientConfig.IsExpired(tokeninfo)))
        elif args.apikey:
            ClientConfig.SaveApiKey(args.environment, args.apikey, args.config)
            print(f"apikey\t{args.apikey}")
        elif args.preferapikey:
            ClientConfig.SetPreferApiKey(args.environment, True, args.config)
            envObj = ClientConfig.GetEnvironment(args.environment)
            print(f"apikey\t{ClientConfig.GetApiKey(envObj)}")

if __name__ == '__main__':
    main()
