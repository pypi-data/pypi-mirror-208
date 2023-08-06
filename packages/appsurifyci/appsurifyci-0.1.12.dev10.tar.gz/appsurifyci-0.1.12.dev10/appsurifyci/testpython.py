azurefilter = "TestCategory=BDDWebSPV&TestCategory=$(TestCategory)&TestCategory=Batch4"

if azurefilter[0:-1].endswith("TestCategory=Batch"):
    azurefilter = azurefilter[0:-19]
print(azurefilter)

testName = "asdftxt"
if "." not in testName:
    testName = ""
print(testName)