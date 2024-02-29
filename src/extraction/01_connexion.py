import pyodbc
import pandas as pd 

from lock_parameters import server, database, username, password


connection = pyodbc.connect(driver='{SQL Server}', host=server, port=1433, database=database,
                      trusted_connection='No', user=username, password=password)

cursor = connection.cursor()

# Sample query
query = """select p.pat_ipp, d.doc_nom, d.doc_creation_date, d.doc_realisation_date, d.doc_stockage_id, fil_data
        from METADONE.metadone.DOCUMENTS d
        left join NOYAU.patient.PATIENT p on d.doc_pat_id = p.pat_id
         left join STOCKAGE.stockage.FILES f on f.fil_id = d.doc_stockage_id
            WHERE doc_nom LIKE '%Anapath%'
            and (p.pat_ipp in ('300307858', '300139098', '300128509', '300216956', '300138147', '300294418', '300252553', '300180068', '300335175', '290004924', '300310211', '300341238', '300325951', '300304877', '300291385', '300335743', '300340686', '300196294', '300323797', '300320279', '300230944', '300335866', '300347429', '300340442', '300305413', '300309674', '300350967', '300228174', '300343285', '300312472', '300196581', '300300756', '300220488', '300337077', '300315570', '300326197', '300338453', '300359634', '300323165', '300303689', '300364288', '300291003', '300345683', '300350022', '300340992', '300342096', '300335294', '300058909', '296024587', '300343468', '300299055', '300367815', '300100024', '300305530', '300336819', '300345359', '300362138', '300329528', '300359051', '300141691', '300351944', '300309133', '300368343', '300247818', '300266344', '300348564', '187083960', '300379278', '300312755', '300381681', '300379470', '300368244', '300378560', '300335659', '300333025', '300326330', '300332754', '300258062', '300363413', '300385697', '300361443', '300201395', '300338660', '300334486', '300306070', '300308871', '300382773', '300287574', '300382500', '300372656', '300447994', '300238645', '300307858', '300652397', '300368810', '300334670', '300370541', '300254828', '297014627', '300336330', '300046115', '300370304', '300397708', '300392223', '300386134', '300395115', '300387261', '300291955', '300399798', '300312562', '300774601', '300379127', '300305571', '300396150', '300400351', '300359550', '300352677', '293024952', '300373860', '183180640', '300112188', '300262247', '300289290', '300377587', '300273006', '300323402', '300405147', '300326888', '300383856', '300406605', '300376244', '291027161', '300091408', '300365805', '300111295', '300406454', '300415128', '300291257', '300350666', '300404588', '300409307', '300334486', '300299799', '300422332', '300423965', '300257095', '300613516', '293021088', '300383174', '300223307', '300424154', '300426827', '300135120', '300335383', '300294426', '300199243', '300294622', '183070370', '300401039', '300383265', '300365694', '300326888', '300376375', '300334173', '300355381', '300406233', '300320792', '300417018', '300124984', '300364476', '300168567', '300415601', '300435800', '300414629', '300432891', '300425795', '300376362', '300394753', '300441636', '300385281', '300426193', '300309012', '300438007', '300420738', '300046861', '300444665', '300290128', '300329722', '300216546', '300449753', '300394182', '291025924', '187083960', '300424643', '300409902', '300407774', '300441665', '300449273', '300353064', '300340881', '300338926', '300438855', '300453369', '300410771', '300369704', '300440486', '300098364', '300325762', '300196294', '300445240', '300446384', '300437432', '300430318', '300445786', '300293259', '300448307', '300466265', '300235183', '300387332', '300465917', '300428963', '300308498', '300444475', '300188938', '300210663', '300457634', '300342662', '300450718', '300409356', '300437113', '300449389', '300409899', '300441509', '300357332', '300489108', '300375539', '300412281', '300471197', '300258661', '300463600', '300385978', '300344555', '300389169', '300455785', '300326330', '300449049', '300460382', '300454831', '300372558', '300091346', '300483493', '300136925', '300451464', '300471009', '300485338', '300430705', '300351271', '300287351', '292019228', '300440763', '300478522', '300453346', '300454106', '300370792', '300401144', '300467556', '300442546', '300491714', '300439243', '300457089', '300314788', '300448706', '300492131', '300461334', '300448039', '300569834', '300500128', '300383130', '300486939', '300470626', '300037312', '300420475', '300490006', '300407222', '300435406', '300492450', '300479774', '300440486', '300231192', '300268219', '300460281', '300397433', '300387355', '300469701', '300508992', '300453747', '300457998', '300312966', '300514542', '300258368', '300439667', '300317307', '300370741', '300388566', '300139951', '300232344', '300180761', '300472617', '300483877', '300279784', '300397649', '300207830', '300364110', '300115897', '300343509', '300421653', '300426322', '300290014', '300419935', '300358928', '300225860', '300510779', '300522373', '300484266', '300505111', '300520369', '300160802', '300457634', '300514646', '300514780', '300513168', '300452521', '300487899', '300002638', '300488245', '300509840', '300386288', '300633013', '300526923', '300539754', '300321382', '300504528', '300385764', '300231410', '300372303', '300468573', '300289563', '300420524', '300536359', '300546511', '300508172', '300506903', '300487437', '300536662', '295001345', '300526298', '300487198', '300550957', '300422736', '300446400', '300248876', '300553661', '300104583', '300521977', '300480933', '300341542', '300517534', '300068030', '300522368', '300548351', '300430705', '300514186', '300538399', '290015939', '300515322', '300514053', '288036003', '300510048', '300409307', '300277322', '300453346', '300557376', '300532910', '300541653', '300536758', '300505731', '300440524', '293021055', '300548207', '300009893', '300442807', '300399498', '300552655', '300417758', '300501271', '300482805', '300208141', '300453701', '300545652', '300563175', '300442089', '300443022', '300567619', '300494389', '300579780', '300568018', '300261229', '300428120', '300580638', '300409152', '300477673', '300041865', '300519481', '300583891', '300383490', '300433053', '300498141', '300518848', '293003735', '300582266', '300449519', '300256138', '300439468', '300396695', '288038628', '300270349', '300590063', '300277057', '300577709', '300545705', '300575191', '300584797', '300581714', '300388452', '300512500', '300596343', '300438855', '300569998', '300571237', '300446746', '300554045', '300398655', '300306053', '300180068', '300536516', '300260951', '300531886', '300594633', '300298286', '300386556', '300417237', '300480655', '300564867', '300596863', '300484399', '300542803', '300539644', '300587197', '300593223', '300596206', '300593602', '300610843', '300591326', '300528539', '300567796', '300385981', '300534099', '300250061', '300447496', '300480235', '300481621', '300585952', '300333223', '300587806', '300585115', '300596753', '291001156', '300504141', '300432499', '300731407', '300175442', '300488605', '300578871', '300593093', '300393652', '300391249', '300567186', '300590028', '300612220', '300242203', '300532730', '300604623', '300629975', '300591432', '300354354', '300421108', '300400879', '300544800', '300611752', '300448291', '300278685', '300621707', '300257687', '300617239', '300620125', '300523132', '300512330', '300597614', '300630283', '300235678', '300421271', '300625923', '300312562', '300639702', '300620686', '300574354', '300559443', '300617825', '300169078', '300540892', '300152500', '300538076', '300646543', '300532241', '300633530', '300613731', '300646643', '300403169', '300627937', '300630393', '300596060', '300611222', '300619422', '300632736', '300345807', '300655769', '300366985', '300630063', '300637753', '300646533', '300650890', '300660202', '300558164', '300645835', '300560088', '300636827', '300647875', '300623649', '300553548', '300607495', '300481029', '300594168', '300655966', '300639470', '300650079', '300657059', '300457271', '300635566', '300343314', '300661549', '300630792', '300671548', '300410042', '300656354', '300668025', '300614648', '300280036', '300560710', '300528262', '300273908', '300641632', '300645667', '300665476', '300644752', '300672984', '300632904', '300525466', '300604923', '300641803', '300648617', '300678775', '300590184', '300666929', '300653751', '300664260', '300336330', '300671508', '300672776', '300633214', '300613002', '300673059', '300656279', '300544962', '300311174', '300663429', '300473817', '300365128', '295001775', '300286484', '300678839', '300594633', '300531232', '297003026', '300684823', '300688770', '300621028', '300553661', '300191107', '300503998', '300479245', '300605783', '300324632', '300676564', '300688023', '300670280', '300645494', '300620686', '300459181', '300682409', '300528848', '300674334', '300665455', '300636414', '300576539', '300562406', '300656959', '300664556', '300700949', '300682227', '300554642', '300705822', '300554737', '300610836', '300368054', '300675753', '300454658', '300668025', '300662088', '300235183', '300499692', '300687572', '300639494', '300712669', '300373860', '300710867', '300643357', '300697198', '300673312', '300545186', '300704921', '300220539', '300721664', '300693265', '300394879', '300573735', '300714039', '300626402', '300721187', '300725646', '300691720', '300725266', '300730902', '300728105', '300720948', '300582393', '300663789', '300668508', '300674334', '300685825', '300739147', '300265948', '300732321', '300735171', '300688032', '300727639', '300728286', '300689136', '300595792', '300673078', '300730411', '300694221', '300375539', '300073074', '300752293', '300744585', '300549371', '300571278', '300743094', '300732450', '300748211', '300729906', '300742191', '300756472', '300716774', '300717050', '300745137', '300756755', '300751886', '300753737', '300739455', '300715997', '300742430', '300750295', '300757756', '300720938', '300760585', '300763402', '300745831', '300761134', '300701581', '300702810', '300735063', '300283099', '300741223', '300061058', '300759846', '300759426', '300748446', '300646540', '300771815', '300723619', '300772312', '300552830', '300758425', '300248876', '0300385764', '0300231410', '0300372303', '0300468573', '0300289563', '0300420524', '0300536359', '0300546511', '0300508172', '0300506903', '0300487437', '0300536662', '0295001345', '0300526298', '0300487198', '0300550957', '0300422736', '0300446400', '0300248876', '0300553661', '0300104583', '0300521977', '0300480933', '0300341542', '0300517534', '0300068030', '0300522368', '0300548351', '0300430705', '0300514186', '0300538399', '0290015939', '0300515322', '0300514053', '0288036003', '0300510048', '0300409307', '0300277322', '0300453346', '0300557376', '0300532910', '0300541653', '0300536758', '0300505731', '0300440524', '0293021055', '0300548207', '0300009893', '0300442807', '0300399498', '0300552655', '0300417758', '0300501271', '0300482805', '0300208141', '0300453701', '0300545652', '0300563175', '0300442089', '0300443022', '0300567619', '0300494389', '0300579780', '0300568018', '0300261229', '0300428120', '0300580638', '0300409152', '0300477673', '0300041865', '0300519481', '0300583891', '0300383490', '0300433053', '0300498141', '0300518848', '0293003735', '0300582266', '0300449519', '0300256138', '0300439468', '0300396695', '0288038628', '0300270349', '0300590063', '0300277057', '0300577709', '0300545705', '0300575191', '0300584797', '0300581714', '0300388452', '0300512500', '0300596343', '0300438855', '0300569998', '0300571237', '0300446746', '0300554045', '0300398655', '0300306053', '0300180068', '0300536516', '0300260951', '0300531886', '0300594633', '0300298286', '0300386556', '0300417237', '0300480655', '0300564867', '0300596863', '0300484399', '0300542803', '0300539644', '0300587197', '0300593223', '0300596206', '0300593602', '0300610843', '0300591326', '0300528539', '0300567796', '0300385981', '0300534099', '0300250061', '0300447496', '0300480235', '0300481621', '0300585952', '0300333223', '0300587806', '0300585115', '0300596753', '0291001156', '0300504141', '0300432499', '0300731407', '0300175442', '0300488605', '0300578871', '0300593093', '0300393652', '0300391249', '0300567186', '0300590028', '0300612220', '0300242203', '0300532730', '0300604623', '0300629975', '0300591432', '0300354354', '0300421108', '0300400879', '0300544800', '0300611752', '0300448291', '0300278685', '0300621707', '0300257687', '0300617239', '0300620125', '0300523132', '0300512330', '0300597614', '0300630283', '0300235678', '0300421271', '0300625923', '0300312562', '0300639702', '0300620686', '0300574354', '0300559443', '0300617825', '0300169078', '0300540892', '0300152500', '0300538076', '0300646543', '0300532241', '0300633530', '0300613731', '0300646643', '0300403169', '0300627937', '0300630393', '0300596060', '0300611222', '0300619422', '0300632736', '0300345807', '0300655769', '0300366985', '0300630063', '0300637753', '0300646533', '0300650890', '0300660202', '0300558164', '0300645835', '0300560088', '0300636827', '0300647875', '0300623649', '0300553548', '0300607495', '0300481029', '0300594168', '0300655966', '0300639470', '0300650079', '0300657059', '0300457271', '0300635566', '0300343314', '0300661549', '0300630792', '0300671548', '0300410042', '0300656354', '0300668025', '0300614648', '0300280036', '0300560710', '0300528262', '0300273908', '0300641632', '0300645667', '0300665476', '0300644752', '0300672984', '0300632904', '0300525466', '0300604923', '0300641803', '0300648617', '0300678775', '0300590184', '0300666929', '0300653751', '0300664260', '0300336330', '0300671508', '0300672776', '0300633214', '0300613002', '0300673059', '0300656279', '0300544962', '0300311174', '0300663429', '0300473817', '0300365128', '0295001775', '0300286484', '0300678839', '0300594633', '0300531232', '0297003026', '0300684823', '0300688770', '0300621028', '0300553661', '0300191107', '0300503998', '0300479245', '0300605783', '0300324632', '0300676564', '0300688023', '0300670280', '0300645494', '0300620686') OR
   p.pat_ipp IN ('0300459181', '0300682409', '0300528848', '0300674334', '0300665455', '0300636414', '0300576539', '0300562406', '0300656959', '0300664556', '0300700949', '0300682227', '0300554642', '0300705822', '0300554737', '0300610836', '0300368054', '0300675753', '0300454658', '0300668025', '0300662088', '0300235183', '0300499692', '0300687572', '0300639494', '0300712669', '0300373860', '0300710867', '0300643357', '0300697198', '0300673312', '0300545186', '0300704921', '0300220539', '0300721664', '0300693265', '0300394879', '0300573735', '0300714039', '0300626402', '0300721187', '0300725646', '0300691720', '0300725266', '0300730902', '0300728105', '0300720948', '0300582393', '0300663789', '0300668508', '0300674334', '0300685825', '0300739147', '0300265948', '0300732321', '0300735171', '0300688032', '0300727639', '0300728286', '0300689136', '0300595792', '0300673078', '0300730411', '0300694221', '0300375539', '0300073074', '0300752293', '0300744585', '0300549371', '0300571278', '0300743094', '0300732450', '0300748211', '0300729906', '0300742191', '0300756472', '0300716774', '0300717050', '0300745137', '0300756755', '0300751886', '0300753737', '0300739455', '0300715997', '0300742430', '0300750295', '0300757756', '0300720938', '0300760585', '0300763402', '0300745831', '0300761134', '0300701581', '0300702810', '0300735063', '0300283099', '0300741223', '0300061058', '0300759846', '0300759426', '0300748446', '0300646540', '0300771815', '0300723619', '0300772312', '0300552830', '0300758425', '0300248876', '0300687426', '0300778494', '0300732297', '0300778053', '0300742733', '0300673788', '0300783342', '0300691771', '0300784537', '0300425057', '0300774265', '0300786750', '0300786035', '0300720539', '0300740900', '0300714809', '0300778683', '0300790631', '0300762782', '0300587806', '0300783936', '0300776452', '0300789642', '0300791538', '0300782310', '0300767904', '0300417349', '0300790037', '0300196294', '0300648617', '0300730570', '0300608408', '0300778682', '0300691478', '0300710706', '0300800193', '0300725869', '0300762184', '0300756114', '0300787576', '0300172114', '0300500110', '0300803413', '0300716568', '0300409135', '0300708014', '0300800061', '0300798286', '0300475035', '0300760662', '0300797918', '0300804237', '0300807301', '0300801616', '0300235678', '0300781899', '0300788327', '0300797105', '0300764275', '0300361879', '0300798390', '0300769206', '0300804379', '0300809859', '0300789569', '0300787620', '0296004187', '0300798014', '0300815661', '0300797398', '0300798194', '0300818023', '0300340825', '0300819706', '0300813671', '0300816402', '0300686389', '0300665750', '0300744745', '0300570512', '0300701098', '0300778391', '0300805188', '0300810203', '0300822913', '0300081558', '0300754859', '0300477915', '0300829351', '0300500888', '0300805229', '0300820478', '0300779189', '0300834354', '0300820928', '0300719412', '0300823006', '0300688275', '0300827285', '0300806237', '0300796804', '0300836782', '0300746309', '0300834503', '0300666621', '0300830528', '0300750254', '0300817008', '0300759036', '0300753991', '0300809393', '0300812606', '0300332754', '0300847665', '0300831867', '0300849290', '0300837963', '0300840888', '0300772042', '0300759919', '0300845870', '0300826152', '0300838518', '0300845915', '0300815915', '0300841675', '0300761559', '300772312'))"""

# Executing the query
with connection.cursor() as cursor:
    cursor.execute(query)
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        if row[5] is not None:
            pat_ipp = row[0]  # Get pat_ipp
            doc_stockage_id = row[4]  # Get doc_stockage_id (original file name)
            fil_data = row[5]  # Get file data
            filename = f"..//..//./data//extract_easily//{pat_ipp}_{doc_stockage_id}.pdf"
            with open(filename, 'wb') as newfile:
                newfile.write(fil_data)
# Closing cursor and connection
cursor.close()
connection.close()