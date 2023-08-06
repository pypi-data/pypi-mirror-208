# Deploy as a Job in Anyscale

### Cluster compute setup

A [Cluster Compute](https://docs.anyscale.com/user-guide/configure/cluster-computes#creating-a-cluster-compute) 
controls the resources of an Anyscale cluster. 

If you want to create/update a cluster compute, build a new compute configuration with the 
command `anyscale cluster-compute`.

### Cluster Environment

A [Cluster Environment](https://docs.anyscale.com/user-guide/configure/dependency-management/anyscale-environments#cluster-environments)
is a build-time definition of a Docker container for the Ray application to run on. 

If you want to create/update a cluster environment, build a new cluster environment with the 
command `anyscale cluster-environment`. 

### Deploy the service as a job

- Package your main application and your GCP credentials file in a folder, and package that 
  in a `.zip` file, and store it in GCS. 

- Package the main `txp` top  level packages in a `.zip` file, and store those in GCS.   

- Define the job [configuration file](https://docs.anyscale.com/user-guide/run-and-monitor/production-jobs#using-production-jobs):
    
  - Setup the `py_modules` options for the `txp` top level packages.
  - Setup the `working_dir` option for  the `working` directory.
  - Setup the job entrypoint.
    
- Launch the Job using the command `anyscale job`.

#### Note about custom Python libraries

If you want to install your library in the Ray runtime environment, you'll need to use one of 
these [alternatives](https://docs.ray.io/en/releases-1.12.0/ray-core/handling-dependencies.html#library-development). 
  
If you want to use your custom `.wheel` package, bear in mind the following constraint, valid as the time of writing
this file:

> Note: This feature is currently limited to modules that are packages with a single directory containing an __init__.py file. 
> For single-file modules, you may use working_dir.

Out current strategy is to use a [`.zip` remote URI](https://docs.ray.io/en/latest/ray-core/handling-dependencies.html#remote-uris) 
for each one of the `txp` top level packages. 
