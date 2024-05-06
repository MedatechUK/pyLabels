import labels 

# Create an A4 portrait (210mm x 297mm) sheets with 3 columns and 7 rows of
# labels. Each label is 63.5mm x 38.1mm with a 2mm rounded corner. The margins are
# automatically calculated.
L7160 = labels.Specification( 
    210
    , 297
    , 3
    , 7
    , 63.5
    , 38.1
    , corner_radius=2
    , top_margin=11 
    , bottom_margin=11
)