import rofunc as rf

# Export a single mvnx file
mvnx_file = '/home/ubuntu/Data/xsens_mvnx/force.mvnx'
rf.xsens.export(mvnx_file, output_type='joint')
