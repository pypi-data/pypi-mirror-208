from playmolecule.datacenter import DataCenter
from playmolecule.session import Session
import zipfile
import shutil
import os


def test_datacenter():
    session = Session(os.environ["TOKEN"])
    dc = DataCenter(session=session)

    tmpfolder = "tmpfolder"
    tmpfile = os.path.join(tmpfolder, "tmpfile.txt")
    tmpzip = "tmpfile.zip"

    outdir = "downloads"

    os.makedirs(tmpfolder, exist_ok=True)

    with open(tmpfile, "w") as f:
        f.write("COOL!")

    with zipfile.ZipFile(tmpzip, "w") as myzip:
        myzip.write(tmpfile, arcname="tmpfile.txt")

    # Test upload file
    fileID = dc.upload_dataset(tmpfile, "test/file.txt")
    filepath = dc.download_dataset(fileID, outdir)

    # Check that the zip doesn't contain other garbage
    assert os.path.relpath(filepath, os.getcwd()) == os.path.join(outdir, "tmpfile.txt")

    with open(filepath, "r") as f:
        assert f.readline().strip() == "COOL!"

    os.remove(filepath)

    # Test re-upload
    newfileID = dc.upload_dataset(tmpfile, "test/file.txt", overwrite=True)
    assert newfileID == fileID

    # Test failed re-upload
    newfileID = dc.upload_dataset(tmpfile, "test/file.txt", overwrite=False)
    assert newfileID is None

    # Test upload folder
    folderID = dc.upload_dataset(tmpfolder, "test/folder")
    filepath = dc.download_dataset(folderID, outdir)

    # Check that the zip doesn't contain the folder name
    assert os.path.relpath(filepath, os.getcwd()) == outdir

    with open(os.path.join(filepath, "tmpfile.txt"), "r") as f:
        assert f.readline().strip() == "COOL!"

    shutil.rmtree(filepath)

    # Test upload zip file
    zipID = dc.upload_dataset(tmpzip, "test/file.zip")
    filepath = dc.download_dataset(zipID, outdir)

    with zipfile.ZipFile(filepath, "r") as myzip:
        myzip.extractall(outdir)

    with open(os.path.join(outdir, "tmpfile.txt"), "r") as f:
        assert f.readline().strip() == "COOL!"

    # Cleanup
    os.remove(tmpzip)
    os.remove(tmpfile)
    shutil.rmtree(tmpfolder)

    assert len(dc.get_datasets(datasetid=fileID, _logger=False)) == 1
    assert len(dc.get_datasets(datasetid=folderID, _logger=False)) == 1
    assert len(dc.get_datasets(datasetid=zipID, _logger=False)) == 1

    dc.remove_dataset(fileID)
    dc.remove_dataset(folderID)
    dc.remove_dataset(zipID)


def test_datacenter_tags():
    session = Session(os.environ["TOKEN"])
    dc = DataCenter(session=session)

    tmpfolder = "tmpfolder"
    tmpfile = os.path.join(tmpfolder, "tmpfile.txt")
    os.makedirs(tmpfolder, exist_ok=True)

    with open(tmpfile, "w") as f:
        f.write("COOL!")

    file0ID = dc.upload_dataset(tmpfile, "test/file0.txt", overwrite=True)
    file1ID = dc.upload_dataset(
        tmpfile, "test/file1.txt", overwrite=True, tags=["test:tag1", "test:tag2"]
    )
    file2ID = dc.upload_dataset(
        tmpfile,
        "test/file2.txt",
        overwrite=True,
        tags=["test:tag2", "test:tag3", "test:tag4"],
    )

    assert len(dc.get_dataset_tags(file0ID)) == 0
    assert len(dc.get_dataset_tags(file1ID)) == 2
    assert len(dc.get_dataset_tags(file2ID)) == 3

    # Test removing a tag
    dc.remove_dataset_tag(file1ID, "test:tag1")
    tags = dc.get_dataset_tags(file1ID)
    assert len(tags) == 1
    assert tags[0] == "test:tag2"

    # Make sure nothing happened to the other dataset tags. Sometimes the tables got wiped by wrong gorm commands
    assert len(dc.get_dataset_tags(file2ID)) == 3

    assert len(dc.get_datasets(tags="test:tag2", _logger=False)) == 2
    assert len(dc.get_datasets(tags="test:tag4", _logger=False)) == 1
    assert len(dc.get_datasets(tags=["test:tag4", "test:tag2"], _logger=False)) == 2
    assert len(dc.get_datasets(taggedonly=True, _logger=False)) > 0
    assert len(dc.get_datasets(tags="test:xxx", _logger=False)) == 0

    # Cleanup
    os.remove(tmpfile)
    shutil.rmtree(tmpfolder)

    # This also checks that nothing breaks when deleting datasets without tags
    dc.remove_dataset(file0ID)
    dc.remove_dataset(file1ID)
    dc.remove_dataset(file2ID)
