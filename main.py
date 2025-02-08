import os
import guitarpro

def merge_gp5_files(input_files, output_file):
    """
    Merge multiple Guitar Pro 5 files into a single GP5 file.
    
    Args:
        input_files (list): List of paths to input GP5 files
        output_file (str): Path where the merged file will be saved
    """
    if not input_files:
        raise ValueError("No input files provided")
    
    try:
        # Load the first file as the base for merging
        merged_song = guitarpro.parse(input_files[0])
        merged_song.title = "Setlist - " + merged_song.title
        merged_song.version = "FICHIER GUITAR PRO v5.00"
    except Exception as e:
        raise Exception(f"Error loading first file {input_files[0]}: {str(e)}")
    
    for file_path in input_files[1:]:
        try:
            current_song = guitarpro.parse(file_path)
            
            # Insert a double bar line before adding new measures
            for track in merged_song.tracks:
                if track.measures:
                    track.measures[-1].header.isDoubleBar = True
            
            # Ensure track alignment: Add missing tracks to the merged song
            for track_idx, track in enumerate(current_song.tracks):
                if track_idx >= len(merged_song.tracks):
                    # If the current song has more tracks, add a new track to the merged song
                    new_track = guitarpro.models.Track(merged_song, len(merged_song.tracks) + 1)
                    new_track.name = track.name  # Preserve track name
                    new_track.channel = track.channel  # Preserve channel settings
                    new_track.isPercussionTrack = track.isPercussionTrack  # Preserve percussion flag
                    merged_song.tracks.append(new_track)
                
                # Extend the measures of the corresponding track
                merged_song.tracks[track_idx].measures.extend(track.measures)
            
            # Add a text marker to indicate song separation
            first_new_measure = len(merged_song.tracks[0].measures) - len(current_song.tracks[0].measures)
            if first_new_measure >= 0:
                for track in merged_song.tracks:
                    if first_new_measure < len(track.measures):
                        measure = track.measures[first_new_measure]
                        measure.text = guitarpro.models.Text(value=f"--- {current_song.title} ---")
            
        except Exception as e:
            print(f"Warning: Error processing {file_path}: {str(e)}")
            continue
    
    try:
        # Ensure the output file has the correct extension
        if not output_file.lower().endswith('.gp5'):
            output_file = output_file.rsplit('.', 1)[0] + '.gp5'
        
        # Save the merged file
        guitarpro.write(merged_song, output_file)
        print(f"Successfully created merged file: {output_file}")
    except Exception as e:
        raise Exception(f"Error saving merged file: {str(e)}")

if __name__ == "__main__":
    folder_path = "setlist_songs/"
    
    # Get all .gp5 files in the folder
    gp5_files = [
        os.path.join(folder_path, f) 
        for f in os.listdir(folder_path) 
        if f.lower().endswith('.gp5')
    ]
    
    # Sort the files alphabetically
    gp5_files.sort()
    
    try:
        # Merge the files
        merge_gp5_files(gp5_files, "merged_setlist.gp5")
    except Exception as e:
        print(f"Error: {str(e)}")