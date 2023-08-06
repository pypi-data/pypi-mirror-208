For using API functionalities of Ango-Hub platform.
    
    from ango.sdk import SDK

    # Init SDK with API key for detailed functioanlities of Ango API https://docs.ango.ai/api/api-documentation
    sdk = SDK(api_key="10541bc8-bed8-4775-8ffc-323eabfcc9ae")
    
    # Upload from local files
    files = ["/home/ofk/Pictures/samples/0003.DCM", "/home/ofk/Pictures/samples/0009.DCM"]
    response = sdk.upload_files("61f8d94a79002950df12234a", files)  # With Project ID
    print(response)
    
    # Or upload from hosted resources
    files = [{
                "data": "https://i.imgur.com/OB0y6MR.jpg",
                "externalId": "111"
            },
            {
                "data": "https://i.imgur.com/CzXTtJV.jpg",
                "externalId": "112"
            }]
    response = sdk.upload_files_cloud("61f8d94a79002950df12234a", files)  # With Project ID
    print(response)

For developing custom plugins that can be integrated to Ango-Hub platform.

    from ango import plugin


    # Create callback function for your plugin. 
    # Input and output definitions are set on Ango-Hub on plugin register
    def callback(data):
        result = model(data)
        return result
    
    
    p = plugins.Plugin("<YOUR_PLUGIN_ID>", "<YOUR_API_KEY>", callback)
    
    plugin.run(p)