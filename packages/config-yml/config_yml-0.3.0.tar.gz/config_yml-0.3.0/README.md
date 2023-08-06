# Config management class
Configuration management package
- Yaml based
- Can use a config template embeded in your application distribution, and a local config (in /home/var/{application})
  customized for your particular installation (that could be edited manually, or by your ansible recipe).
- Local config will be merged with the template in your application overwritting its values, allowing you to upgrade 
  and distribute your application adding new fields with default values seamlessly.
- Provides functionality not only to read the configuration, but also to modify it in runtime
