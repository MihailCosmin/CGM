﻿using System;
using System.IO;
using codessentials.CGM.Export;
using codessentials.CGM.Import;

namespace codessentials.CGM
{
    /// <summary>
    /// Represents a CGM file in binary mode
    /// </summary>
    public class BinaryCgmFile : CgmFile
    {
        /// <summary>
        /// The binary file name
        /// </summary>
        public string FileName { get; }

        public BinaryCgmFile()
        {
            Name = "new";
        }

        /// <summary>
        /// Creates a new CGM object reading a binary CGM file.
        /// </summary>
        /// <param name="fileName">Path to the binary CGM file.</param>
        public BinaryCgmFile(string fileName)
        {
            FileName = fileName;
            Name = Path.GetFileName(fileName);

            ReadData(fileName);
        }

        /// <summary>
        /// Creates a new CGM object read from a stream.
        /// </summary>
        /// <param name="data">The stream containing binary CGM data.</param>
        /// <param name="name">The name of the CGM.</param>
        public BinaryCgmFile(Stream data, string name = "stream")
        {
            if (data is null)
                throw new ArgumentNullException(nameof(data));

            Name = name;
            ReadData(data);
        }

        /// <summary>
        /// Writes the CGM commands to the current file name
        /// </summary>
        public void WriteFile()
        {
            WriteFile(FileName);
        }

        /// <summary>
        /// Writes the CGM commands to the given file name-
        /// </summary>
        /// <param name="fileName">The file name to write the content to.</param>
        public void WriteFile(string fileName)
        {
            using var stream = File.Create(fileName);
            WriteFile(stream);
        }

        /// <summary>
        /// Writes the CGM commands to the given stream-
        /// </summary>
        /// <param name="stream">The stream to write the content to.</param>
        public void WriteFile(Stream stream)
        {
            ResetMetaDefinitions();

            using var writer = new DefaultBinaryWriter(stream, this);
            foreach (var command in _commands)
                writer.WriteCommand(command);

            _messages.AddRange(writer.Messages);
        }

        /// <summary>
        /// Gets the whole CGM as byte array.
        /// </summary>
        /// <returns></returns>
        public byte[] GetContent()
        {
            using var stream = new MemoryStream();
            WriteFile(stream);

            return stream.ToArray();
        }

        private void ReadData(Stream stream)
        {
            ResetMetaDefinitions();
            using var reader = new DefaultBinaryReader(stream, this, new DefaultCommandFactory());
            reader.ReadCommands();

            _messages.AddRange(reader.Messages);
        }

        private void ReadData(string fileName)
        {
            using var stream = File.OpenRead(fileName);
            ReadData(stream);
        }
    }
}
