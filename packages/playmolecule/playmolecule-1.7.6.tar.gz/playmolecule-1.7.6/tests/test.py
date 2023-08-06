# from playmolecule import Session, JobStatus


# def test_protprep():
#     s = Session("admin_token")
#     app = s.start_app("ProteinPrepare")
#     app.pdb = "3ptb"
#     app.submit()
#     app.get_status()
#     app.retrieve(path="/tmp/", on_status=JobStatus.COMPLETED)


# def test_mdrun():
#     pass


# def test_simplerun():
#     s = Session("admin_token")
#     app = s.start_app("SimpleRun")
#     app.describe()
#     app.inputdir = "./test-simplerun/build_alanine_dipeptide_amber/"
#     app.runtime = 1
#     app.numruns = 1
#     app.equiltime = "1"
#     app.simtype = "globular"
#     app.submit()
#     app.wait_children()
#     app.retrieve(path="/tmp/", on_status=JobStatus.COMPLETED)


# def test_kdeep():
#     s = Session("admin_token")
#     app = s.start_app("Kdeep")
#     app.pdb = "./pdbs/4uai/4uai_prot.pdb"
#     app.sdf = "./pdbs/4uai/4uai_3gg.sdf"
#     app.submit()


# def test_ligdream():
#     s = Session("admin_token")
#     app = s.start_app("LigDream")
#     app.input = "./pdbs/3ptb/3ptb_ben.sdf"
#     app.submit()


# def test_ligann():
#     s = Session("admin_token")
#     app = s.start_app("LiGAN")
#     app.pdbs = "./test-ligann/4uai_prot.zip"
#     app.centers = "./test-ligann/4uai_centers.csv"
#     app.nprotgen = 1
#     app.nligdecode = 1
#     app.submit()


# def test_adaptive():
#     s = Session("admin_token")
#     app = s.start_app("AdaptiveSampling")
#     app.inputdir = "test/generators/"
#     app.numepochs = 3
#     app.nmin = 1
#     app.nmax = 2
#     app.adapttype = "protconf"
#     app.metric = "dihedrals"
#     app.submit()
