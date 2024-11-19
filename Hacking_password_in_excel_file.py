# this script creates a bin file from a zip file containing an excel file 
# with a password on it. thne modifies the part of teh file that has the 
# password and disables it. thne in saves it back to a ZIP file

# then you can unzip the new zip file and teh wxcel file will not have '
# the password on it.

#%%
import zipfile
import io
#%%

def modify_bin_in_zip(zip_path, bin_filename, modify_func):
    # Open the ZIP file in read mode
    with zipfile.ZipFile(zip_path, 'r') as zip_read:
        # Create a copy of the ZIP file's contents in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_write:
            for item in zip_read.infolist():
                # Read each file in the ZIP
                data = zip_read.read(item.filename)
                if item.filename == bin_filename:
                    # Modify the .bin file
                    data = modify_func(data)
                # Write the (possibly modified) data to the new ZIP
                zip_write.writestr(item, data)

    # Save the modified ZIP file
    with open(zip_path, 'wb') as f:
        f.write(zip_buffer.getvalue())

def mod_func(data):
    # Replace the byte sequence "DPB" with "DPx"
    search_bytes = b"DPB"
    replace_bytes = b"DPx"
    return data.replace(search_bytes, replace_bytes)

# Path to your ZIP file and the .bin file within it
zip_path = r'C:\GPM_CD\07-Python\inputs\BHPODSeepageManagement.zip'
bin_filename = 'xl/vbaProject.bin'

# Modify the .bin file within the ZIP file
modify_bin_in_zip(zip_path, bin_filename, mod_func)

print('File modified successfully !!')
#%%