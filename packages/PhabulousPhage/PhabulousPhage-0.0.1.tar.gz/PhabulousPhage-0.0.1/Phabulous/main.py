def main():

    import os
    import sys
    import pandas as pd
    import random
    import csv
    import argparse
    from pycirclize import Circos
    from pycirclize.parser import Genbank
    import matplotlib.colors as mcolors
    from matplotlib.patches import Patch

    class Feature(object):
        def __init__(self, id, length, phrog, category, product, start, end, gbkn):
            self.id = id;
            self.length = length;
            self.phrog = phrog;
            self.category = category;
            self.product = product;
            self.start = start;
            self.end = end;
            self.gbkn = gbkn;

    class Pair(object):
        def __init__(self, name, gbk, protein):
            self.name = name;
            self.gbk = gbk;
            self.protein = protein;

    # Defining function to assign proteins from csv
    def assign_proteins(protein_csv):
        
        lysogeny = []
        packaging = []
        transcription = []
        connectors = []
        tail = []
        lysis =[]
        nucl_metabolism = []
        other = []
        unknown = []
        auxiliary = []
        no_phrog = []
        
        for index, row in protein_csv.iterrows():
            if row["category"] == "integration and excision":
                lysogeny.append(row['product'])
            if row["category"] == "head and packaging":
                packaging.append(row['product'])
            if row["category"] == "transcription regulation":
                transcription.append(row['product'])
            if row["category"] == "connector":
                connectors.append(row['product'])
            if row["category"] == "tail":
                tail.append(row['product'])
            if row["category"] == "lysis":
                lysis.append(row['product'])
            if row["category"] == "DNA, RNA and nucleotide metabolism":
                nucl_metabolism.append(row['product'])
            if row["category"] == "other":
                other.append(row['product'])     
            if row["category"] == "unknown function":
                unknown.append(row['product'])
            if row["category"] == "moron, auxiliary metabolic gene and host takeover":
                auxiliary.append(row['product'])
            if row["category"] == "No phrog":
                no_phrog.append(row['product'])
        
        lysogeny = tuple(lysogeny)
        packaging = tuple(packaging)
        transcription = tuple(transcription)
        connectors = tuple(connectors)
        tail = tuple(tail)
        lysis =tuple(lysis)
        nucl_metabolism = tuple(nucl_metabolism)
        other = tuple(other)
        unknown = tuple(unknown)
        auxiliary = tuple(auxiliary)
        no_phrog = tuple(no_phrog)
        
        return lysogeny, packaging, transcription, connectors, tail, lysis, nucl_metabolism, other, unknown, auxiliary, no_phrog
        
    # Creating function to input face colours
    def custom_face_colours(feature):
        product_name = feature.qualifiers.get("product", [""])[0]
        if product_name.startswith(lysogeny):
            return colour_1
        elif product_name.startswith(packaging):
            return colour_2
        elif product_name.startswith(transcription):
            return colour_3
        elif product_name.startswith(connectors):
            return colour_4
        elif product_name.startswith(tail):
            return colour_5
        elif product_name.startswith(lysis):
            return colour_6
        elif product_name.startswith(nucl_metabolism):
            return colour_7
        elif product_name.startswith(other):
            return colour_8
        elif product_name.startswith(unknown):
            return colour_9
        elif product_name.startswith(auxiliary):
            return colour_10
        elif product_name.startswith(no_phrog):
            if "tRNA" in product_name:
                return "grey"
            else:
                return "grey"
        else:
            return "grey"

    # Creating colour assignment function for links
    def assign_colours(feature):
        if feature.startswith(lysogeny):
            return A['colour']
        elif feature.startswith(packaging):
            return B['colour']
        elif feature.startswith(transcription):
            return C['colour']
        elif feature.startswith(connectors):
            return D['colour']
        elif feature.startswith(tail):
            return E['colour']
        elif feature.startswith(lysis):
            return F['colour']
        elif feature.startswith(nucl_metabolism):
            return G['colour']
        elif feature.startswith(other):
            return H['colour']
        elif feature.startswith(unknown):
            return I['colour']
        elif feature.startswith(auxiliary):
            return J['colour']
        elif feature.startswith(no_phrog):
            if "tRNA" in feature:
                return "black"
            else:
                return "grey"
        else:
            return "grey"

    def plot_links(feature_set_1, feature_set_2):
        phrog_set1 = set()
        phrog_set2 = set()
        dup1 = []
        dup2 = []
        
        for feature in feature_set_1:
            if feature.phrog in phrog_set1:
                dup1.append(feature)
                continue
            phrog_set1.add(feature.phrog)

        for feature in feature_set_2:
            if feature.phrog in phrog_set2:
                dup2.append(feature)
                continue
            phrog_set2.add(feature.phrog)

        # Matching features based on phrog values
        matched_list = []

        for phrog in phrog_set1.intersection(phrog_set2):
            
            matched_features1 = [feature for feature in feature_set_1 if feature.phrog == phrog]
            matched_features2 = [feature for feature in feature_set_2 if feature.phrog == phrog]
            
            if len(matched_features1) == 1 and len(matched_features2) == 1:
                matched_list.append((matched_features1[0], matched_features2[0]))

        # Adding links
        for m1, m2 in matched_list:
            
            col = assign_colours(m1.product)
            
            link1 = (m1.gbkn, m1.start, m1.end)
            link2 = (m2.gbkn, m2.start, m2.end)
            
            circos.link(link1, link2, color=col, direction=1)

    # Write file functions
    def create_csv(filename, data):
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(data)

    def append_csv(filename, data):
        with open(filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data)

    # Creating function to check directory path
    def valid_dir(dir_path):
        if not os.path.isdir(dir_path):
            raise argparse.ArgumentTypeError(
                f"{dir_path} is not a valid directory path")
        if not os.access(dir_path, os.R_OK):
            raise argparse.ArgumentTypeError(
                f"{dir_path} is not a readable directory")
        return dir_path

    # Setting arguments
    parser = argparse.ArgumentParser(description='Josh Iszatt, easy image generation package. 2023')
    parser.add_argument('-i', '--input', type=valid_dir,
                        required=True, help='Path to the input files (gbk) and proteins (if available)')
    parser.add_argument('-o', '--output', type=valid_dir,
                        required=True, help='Path to the output directory')
    parser.add_argument('-c', '--colours', type=str, choices=['sunset','iridescent','noir','random', 'custom'], 
                        help='Colour scheme')
    parser.add_argument('--outer_ring', type=str, default='grey',
                        choices=['light', 'grey', 'dark'], help='Choose an outer ring colour')
    parser.add_argument('--inner_ring', type=str, default='skyblue',
                        choices=['tomato', 'skyblue', 'limegreen', 'white'], help='Choose an inner ring colour')
    parser.add_argument('-s', '--style', type=str, default='arrow',
                        choices=['arrow', 'box'], help='Choose a track style')
    parser.add_argument('--intervals', type=int, default=40000,
                        help='Specify genome interval range')
    parser.add_argument('--dpi', type=int, default=300,
                        help='Specify image quality in dots per inch')
    parser.add_argument('--name', type=str, default='Phage_image',
                        help='Image name')

    # Adding functional data
    parser.add_argument('--feature_highlight', type=str, help='Highight a feature category')
    parser.add_argument('--genome_highlight', type=str, help='Highight a genome (using its name)')

    # Adding flag


    # Printing and parsing arguments
    print("Command given:", sys.argv, sep='\n')
    args = parser.parse_args()

    if args.outer_ring == 'light':
        bck_1 = 'white'
        txt_1 = 'black'
        bck_2 = 'black'
        txt_2 = 'white'
    elif args.outer_ring == 'grey':
        bck_1 = 'grey'
        txt_1 = 'black'
        bck_2 = 'black'
        txt_2 = 'white'
    elif args.outer_ring == 'dark':
        bck_1 = 'black'
        txt_1 = 'white'
        bck_2 = 'tomato'
        txt_2 = 'black'

    # Setting colour scheme
    if args.colours == "sunset":
        colour_1 = "#f3a683"
        colour_2 = "#f7d794"
        colour_3 = "#f5cd79"
        colour_4 = "#fc9d9a"
        colour_5 = "#e77f67"
        colour_6 = "#db3a1b"
        colour_7 = "#c4270c"
        colour_8 = "#c44569"
        colour_9 = "#d6a2e8"
        colour_10 = "#8d6e63"
    elif args.colours == "iridescent":
        colour_1 = "blueviolet"
        colour_2 = "mediumorchid"
        colour_3 = "mediumslateblue"
        colour_4 = "slateblue"
        colour_5 = "royalblue"
        colour_6 = "dodgerblue"
        colour_7 = "steelblue"
        colour_8 = "cornflowerblue"
        colour_9 = "skyblue"
        colour_10 = "lightblue"
    elif args.colours == "noir":
        colour_1 = "#222222"
        colour_2 = "#444444"
        colour_3 = "#666666"
        colour_4 = "#888888"
        colour_5 = "#aaaaaa"
        colour_6 = "#cccccc"
        colour_7 = "#dddddd"
        colour_8 = "#eeeeee"
        colour_9 = "#f0f0f0"
        colour_10 = "#ffffff"
    elif args.colours == "random":
        colours = list(mcolors.CSS4_COLORS.keys())
        random.shuffle(colours)
        colour_1, colour_2, colour_3, colour_4, colour_5, colour_6, colour_7, colour_8, colour_9, colour_10 = colours[:10]
    else:
        colour_1 = "lightgrey"
        colour_2 = "lightgrey"
        colour_3 = "lightgrey"
        colour_4 = "lightgrey"
        colour_5 = "lightgrey"
        colour_6 = "lightgrey"
        colour_7 = "lightgrey"
        colour_8 = "lightgrey"
        colour_9 = "lightgrey"
        colour_10 = "lightgrey"

    A = {'name': 'lysogeny','colour': colour_1}
    B = {'name': 'packaging', 'colour': colour_2}
    C = {'name': 'transcription', 'colour': colour_3}
    D = {'name': 'connectors', 'colour': colour_4}
    E = {'name': 'tail', 'colour': colour_5}
    F = {'name': 'lysis', 'colour': colour_6}
    G = {'name': 'nucl_metabolism', 'colour': colour_7}
    H = {'name': 'other', 'colour': colour_8}
    I = {'name': 'unknown', 'colour': colour_9}
    J = {'name': 'auxiliary', 'colour': colour_10}
    feature_categories = [A,B,C,D,E,F,G,H,I,J]

    if args.colours == 'custom':
        colours = f"{args.input}/colours.csv"
        if os.path.isfile(colours):
            colours_df = pd.read_csv(colours)
            print("Using custom colours")
            for cat in feature_categories:
                for index, row in colours_df.iterrows():
                    if cat['name'] == row['feature']:
                        cat['colour'] = row['colour']
        else:
            print(f"Cannot find colours.csv file within {args.input} directory")
            sys.exit(1)

    if args.feature_highlight:
        for category in feature_categories:
            if category['name'] == args.feature_highlight:
                print(f"Highlighting the {args.feature_highlight} feature links")
                category['colour'] = 'red'

    pairs = []
    for file in os.listdir(args.input):
        filepath = os.path.join(args.input, file)
        
        if os.path.isfile(filepath):
            
            if file.endswith(".gbk"):
                name = file[:-4]
                proteins = f"{name}_proteins.csv"
                protein_filepath = os.path.join(args.input, proteins)
                
                if os.path.isfile(protein_filepath):
                    file_pair = Pair(name, filepath, protein_filepath)
                    pairs.append(file_pair)
                else:
                    file_pair = Pair(name, filepath, None)
                    pairs.append(file_pair)

    # Report pairs
    count = len(pairs)
    if count < 2:
        sys.exit("ERROR, less than 2 gbk files found")

    # Creating sector dictionaries
    sectors = {}
    name2pairs = {}
    names = []
    for pair in pairs:
        
        # Reading gbk file to obtain name
        gbk = Genbank(pair.gbk)
        
        # Adding sectors and pair dictionary
        sectors[gbk.name] = gbk.range_size
        name2pairs[gbk.name] = pair
        
        names.append(gbk.name)
        
        if pair.protein is None and args.colours:
            sys.exit("Protein file does not exist for one or more pairs\nColours cannot be assigned")
            
        if pair.protein is None and args.genome_highlight:
            print(f"Protein file does not exist, {args.genome_highlight} links cannot be drawn")
            
        if pair.protein is None and args.feature_highlight:
            sys.exit(f"Protein file does not exist, {args.feature_highlight} cannot be drawn")


    if args.genome_highlight:
        if args.genome_highlight not in names:
            print(f"{args.genome_highlight} is not here or spelled incorrectly\nThese are the names:")
            print(names)
            sys.exit(1)

    # Creating image with sectors
    circos = Circos(sectors, space=2)

    # Looping through sectors and adding tracks
    all_features = []
    for sector in circos.sectors:
        
        # Pulling pairs
        pair = name2pairs[sector.name]
        
        # Reading files
        gbk = Genbank(pair.gbk)
        
        # Assigning proteins
        if pair.protein is not None:
            df = pd.read_csv(pair.protein)
            lysogeny, packaging, transcription, connectors, tail, lysis, nucl_metabolism, other, unknown, auxiliary, no_phrog = assign_proteins(df)
    
        # Creating first track
        track_1 = sector.add_track((95, 100))    
        if sector.name == args.genome_highlight:
            track_1.axis(fc=bck_2)
            track_1.text(sector.name, color=txt_2, size=10)
        else:
            track_1.axis(fc=bck_1)
            track_1.text(sector.name, color=txt_1, size=10)
            
        track_1.xticks_by_interval(args.intervals)
                
        # Creating fwd note track
        feature_note = sector.add_track((85, 90))
        feature_note.axis(fc=args.inner_ring)
        feature_note.text("Features", color="black", size=10)
        
        # Creating fwd feature track
        fwd_feature_track = sector.add_track((80, 85))
        rev_feature_track = sector.add_track((75, 80))
        
        if args.colours:
            fwd_feature_track.genomic_features(gbk.extract_features("CDS", target_strand=1), 
                                            plotstyle=args.style, 
                                            facecolor_handler=custom_face_colours)
            rev_feature_track.genomic_features(gbk.extract_features("CDS", target_strand=-1), 
                                            plotstyle=args.style, 
                                            facecolor_handler=custom_face_colours)
        else:
            fwd_feature_track.genomic_features(gbk.extract_features("CDS", target_strand=1), 
                                            plotstyle=args.style, 
                                            fc='red')
            rev_feature_track.genomic_features(gbk.extract_features("CDS", target_strand=-1), 
                                            plotstyle=args.style, 
                                            fc='blue')

        # Obtaining list of features for links
        if pair.protein is not None:
            features = []
            for index, row in df.iterrows():
                feature = Feature(
                    row['locus_tag'],
                    row['length_bp'],
                    row['EC_number'],
                    row['category'],
                    row['product'],
                    row['start'],
                    row['end'],
                    gbk.name
                )
                features.append(feature)
        
            # Adding features to all features tuple
            all_features.append(features)

    # Drawing links
    for feature_set in all_features:
        if feature_set[0].gbkn == args.genome_highlight:
            for f in all_features:
                if not f[0].gbkn == args.genome_highlight:
                    plot_links(feature_set, f)

    fig = circos.plotfig()

    # Add figure legend
    if args.colours:
        
        handles = [
            Patch(color=A['colour'], label="Lysogeny"),
            Patch(color=B['colour'], label="packaging"),
            Patch(color=C['colour'], label="transcription"),
            Patch(color=D['colour'], label="connectors"),
            Patch(color=E['colour'], label="tail"),
            Patch(color=F['colour'], label="lysis"),
            Patch(color=G['colour'], label="nucleotide metabolism"),
            Patch(color=H['colour'], label="other"),
            Patch(color=I['colour'], label="unknown"),
            Patch(color=J['colour'], label="auxiliary")
            ]

        legend = fig.legend(
            title='Feature colours:        ',
            handles=handles, 
            bbox_to_anchor=(-0.25, 0.6), 
            loc='center left',
            fontsize=10)
    else:
        handles = [
            Patch(color='red', label="Forward CDS"),
            Patch(color='blue', label="Reverse CDS")
            ]
            
        legend = fig.legend(
            title='Feature colours:',
            handles=handles, 
            bbox_to_anchor=(-0.25, 0.6), 
            loc='center left',
            fontsize=10)

    # Saving to disk
    fig.savefig(f"{args.output}/{args.name}.png", dpi = args.dpi)

    # Option to save colours
    if args.colours == "random":
        decision = input('Save colours?')
        print(decision)

        valid = ['y','Y','yes','YES', 'Yes']
        invalid = ['n','N','no','NO', 'No']

        if decision in valid:
            print('Saving colour profile as "colours.csv"')
            file = f"{args.output}/colours.csv"
            headers = [['feature','colour']]
            
            create_csv(file, headers)
            
            colours = [['lysogeny', colour_1], 
                    ['packaging', colour_2], 
                    ['transcription', colour_3], 
                    ['connectors', colour_4], 
                    ['tail', colour_5], 
                    ['lysis', colour_6], 
                    ['nucl_metabolism', colour_7], 
                    ['other', colour_8], 
                    ['unknown', colour_9], 
                    ['auxiliary', colour_10],
                    ['no_phrog', 'grey']]
            
            for colour in colours:
                append_csv(file, [colour[0], colour[1]])
            
            print(colour_1, colour_2, colour_3, colour_4, colour_5, colour_6, colour_7, colour_8, colour_9, colour_10, sep='\n')
        elif decision in invalid:
            print('Discarding colour profile')
        else:
            print('Unsure what that was...')

if __name__ == "__main__":
    exit(main())
